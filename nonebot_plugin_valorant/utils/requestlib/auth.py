import re
import ssl
import json
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from typing import Any, Dict, Tuple, Optional

import aiohttp as aiohttp
import urllib3.exceptions
from pydantic import BaseModel

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.utils import message_translator
from nonebot_plugin_valorant.utils.errors import (
    ResponseError,
    DataParseError,
    AuthenticationError,
)

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROXY = plugin_config.valorant_proxies


class AuthCredentials(BaseModel):
    """
    A class representing authentication token for Valorant API.

    Attributes:
        access_token (str): The API access token.
        token_id (str): The ID of the token.
        expiry_token (str): The duration in seconds for the token to expire.
        entitlements_token (str): The token for accessing entitlements.

    """

    access_token: Optional[str] = None
    token_id: Optional[str] = None
    expiry_token: Optional[int] = None
    entitlements_token: Optional[str] = None
    cookie: Optional[Dict] = None


# https://developers.cloudflare.com/ssl/ssl-tls/cipher-suites/
FORCED_CIPHERS = [
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-SHA256",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-RSA-AES256-SHA",
    "ECDHE-ECDSA-AES128-SHA256",
    "ECDHE-ECDSA-AES128-SHA",
    "ECDHE-ECDSA-AES256-SHA",
    "ECDHE+AES128",
    "ECDHE+AES256",
    "ECDHE+3DES",
    "RSA+AES128",
    "RSA+AES256",
    "RSA+3DES",
]


class ClientSession(aiohttp.ClientSession):
    """
    A subclass of aiohttp.ClientSession with additional configurations for TLS encryption and authentication.

    Attributes:
        None

    Methods:
        - __init__(*args, **kwargs): Initialize a ClientSession object with custom configurations.

        Note: This class inherits all methods and attributes from aiohttp.ClientSession.

    Example:
        # Create a ClientSession object with default configurations
        session = ClientSession()
    """

    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3

        ctx.set_ciphers(":".join(FORCED_CIPHERS))

        super().__init__(
            *args,
            **kwargs,
            cookie_jar=aiohttp.CookieJar(),
            connector=aiohttp.TCPConnector(ssl=ctx),
        )


class Auth:
    RIOT_CLIENT_USER_AGENT = (
        "RiotClient/60.0.6.4770705.4749685 rso-auth (Windows;10;;Professional, x64)"
    )
    AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"

    def __init__(self) -> None:
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": Auth.RIOT_CLIENT_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
        }
        self.user_agent: str = Auth.RIOT_CLIENT_USER_AGENT
        self.locale_code = "en-US"  # default language

    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """用于认证用户的函数。

        Args:
            username: 要认证的用户名。
            password: 要认证的密码。

        Returns:
            如果认证成功，则返回包含认证数据的字典，包括 cookie、访问令牌和令牌 ID。
            如果认证需要 2FA，则此函数返回一个包含 cookie 数据和提示用户输入 2FA
            的消息的字典。否则，此函数返回 None。

        Raises:
            AuthenticationError: 如果认证失败。
        """

        session = ClientSession()

        # 准备初始授权请求的数据。
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            "scope": "account openid",
        }

        # 发送初始授权请求。
        response = await session.post(
            self.AUTH_URL,
            json=data,
            headers=self.headers,
            proxy=PROXY,
        )

        # 准备授权请求的 cookies。
        cookies = {"cookie": {}}
        if response.status == 403:
            raise AuthenticationError(message_translator("errors.AUTH.BLOCKED"))
        for cookie in response.cookies.items():
            cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

        # 准备身份验证请求的数据。
        data = {
            "type": "auth",
            "username": username,
            "password": password,
            "remember": True,
        }

        # 发送身份验证请求。
        async with session.put(
            self.AUTH_URL,
            json=data,
            headers=self.headers,
            cookies=cookies["cookie"],
            proxy=PROXY,
        ) as response:
            data = await response.json()
            for cookie in response.cookies.items():
                cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

        # 关闭会话。
        await session.close()
        # 请求过多返回"error" = "rate_limited"
        if data.get("error") == "rate_limited":
            raise AuthenticationError(message_translator("errors.AUTH.RATELIMIT"))
        # 处理身份验证响应。
        if data["type"] == "response":
            # 如果身份验证成功，则从响应中提取令牌。
            access_token, token_id, _ = self._extract_tokens_from_response(data)

            # 设置令牌的到期时间。
            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies["cookie"]["expiry_token"] = int(datetime.timestamp(expiry_token))

            # 返回认证数据。
            return {
                "auth": "response",
                "data": {
                    "cookie": cookies,
                    "access_token": access_token,
                    "token_id": token_id,
                    "expiry_token": int(datetime.timestamp(expiry_token)),
                },
            }
        elif data["type"] == "multifactor":
            # 2FA 验证流程。
            if response.status == 429:
                # 短时间内大量重试触发RATELIMIT
                raise AuthenticationError(message_translator("errors.AUTH.RATELIMIT"))

            method = data["multifactor"]["method"]
            if method == "email":
                # 如果身份验证需要基于电子邮件的 2FA 代码，则返回必要的数据。
                return {
                    "auth": "2fa",
                    "cookie": cookies,
                    "email": f"{data['multifactor']['email']}",
                }
            else:
                # 如果身份验证需要基于不支持的 2FA 方法，则引发 AuthenticationError。
                raise AuthenticationError(
                    message_translator("errors.AUTH.TEMP_LOGIN_NOT_SUPPORT_2FA")
                )
        else:
            # 如果身份验证失败，则引发 AuthenticationError。
            raise AuthenticationError(
                message_translator("errors.AUTH.INVALID_PASSWORD")
            )

    async def auth_by_code(self, code: str, cookies: Dict) -> Dict[str, Any]:
        """用于输入 2FA 验证码的方法。

        Args:
            code: 2FA 验证码。
            cookies: 包含 Cookie 的字典。

        Returns:
            包含身份验证信息的字典。

        Raises:
            AuthenticationError: 如果输入的 2FA 验证码无效。
        """

        session = ClientSession()

        # 准备请求体。
        # noinspection SpellCheckingInspection
        data = {"type": "multifactor", "code": code, "rememberDevice": True}

        # 发送输入 2FA 验证码请求。
        async with session.put(
            self.AUTH_URL,
            headers=self.headers,
            json=data,
            cookies=cookies["cookie"],
        ) as r:
            data = await r.json()

        # 关闭会话。
        await session.close()

        # 如果成功输入 2FA 验证码，则返回包含身份验证信息的字典。
        if data["type"] == "response":
            cookies = {"cookie": {}}
            for cookie in r.cookies.items():
                cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

            uri = data["response"]["parameters"]["uri"]
            access_token, token_id = self._extract_tokens_from_uri(uri)
            expiry_token = datetime.timestamp(datetime.now() + timedelta(minutes=59))

            return {
                "auth": "response",
                "data": {
                    "cookie": cookies,
                    "access_token": access_token,
                    "token_id": token_id,
                    "expiry_token": int(expiry_token),
                },
            }
        raise AuthenticationError(message_translator("errors.AUTH.2FA_INVALID_CODE"))

    async def redeem_cookies(self, cookies: Dict) -> AuthCredentials:
        """
        该函数用于兑换 cookies。

        Args:
            self:
            cookies: 包含 cookies 的字典。

        Returns:

        Raises:
            如果 cookies 过期则会抛出 AuthenticationError。
        """

        # 将字符串类型的 cookies 转为字典类型
        if isinstance(cookies, str):
            cookies = json.loads(cookies)

        # 创建一个新的 HTTP 会话
        session = ClientSession()

        # 取出 cookies
        if "cookie" in cookies:
            cookies = cookies["cookie"]

        # 向 Riot 的验证网站发送请求
        async with session.get(
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in&client_id"
            "=play"
            "-valorant-web-prod&response_type=token%20id_token&scope=account%20openid&nonce=1",
            cookies=cookies,
            allow_redirects=False,
        ) as r:
            data = await r.text()

        # 如果 HTTP 状态码不为 303 或者响应的 Location 以 /auth 开头则说明 cookies 过期，抛出 AuthenticationError
        if r.status != 303:
            raise AuthenticationError(message_translator("errors.AUTH.COOKIES_EXPIRED"))

        if r.headers["Location"].startswith("/auth"):
            raise AuthenticationError(message_translator("errors.AUTH.COOKIES_EXPIRED"))

        # 复制原有 cookies
        old_cookie = cookies.copy()

        # 更新 cookies
        new_cookies = {"cookie": old_cookie}
        for cookie in r.cookies.items():
            new_cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

        await session.close()

        access_token, token_id = self._extract_tokens_from_uri(data)
        entitlements_token = await self.get_entitlements_token(access_token)
        expiry_token = int(datetime.timestamp(datetime.now() + timedelta(minutes=59)))

        return AuthCredentials(
            access_token=access_token,
            token_id=token_id,
            entitlements_token=entitlements_token,
            cookie=new_cookies,
            expiry_token=expiry_token,
        )

    async def temp_auth(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        临时登录，返回包含玩家信息的字典。

        Args:
            username (str): 玩家账号。
            password (str): 玩家密码。

        Returns:
            包含兑换后的 cookies、access token 和 entitlements token 的字典。
        Raises:
            AuthenticationError:
        """
        authenticate = await self.authenticate(username, password)
        if authenticate["auth"] == "response":
            access_token = authenticate["data"]["access_token"]
            token_id = authenticate["data"]["token_id"]

            entitlements_token = await self.get_entitlements_token(access_token)
            puuid, name, tag = await self.get_userinfo(access_token)
            region = await self.get_region(access_token, token_id)
            player_name = f"{name}#{tag}" if tag and name else "no_username"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Riot-Entitlements-JWT": entitlements_token,
            }
            return {
                "puuid": puuid,
                "region": region,
                "headers": headers,
                "player_name": player_name,
            }
        raise AuthenticationError(
            message_translator("errors.AUTH.TEMP_LOGIN_NOT_SUPPORT_2FA")
        )

    async def login_with_cookie(self, cookies: Dict) -> AuthCredentials:
        """
        使用 Cookie 进行登录并返回包含访问令牌、令牌 ID 和资格令牌的字典。

        Args:
            cookies (Dict): 包含 Cookie 的字典。

        Returns:
            dict: 包含访问令牌、令牌 ID、资格令牌和 Cookie 等字段的字典。

        Raises:
            AuthenticationError: 如果登录失败，则会引发异常。
        """
        # 构建 Cookie 负载
        cookie_value = cookies.get("cookie", "")
        cookie_payload = (
            f"ssid={cookie_value};" if cookie_value.startswith("e") else cookie_value
        )

        # 将 Cookie 加入请求头
        self.headers["cookie"] = cookie_payload

        session = ClientSession()

        # 发送登录请求
        r = await session.get(
            "https://auth.riotgames.com/authorize"
            "?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in"
            "&client_id=play-valorant-web-prod"
            "&response_type=token%20id_token"
            "&scope=account%20openid"
            "&nonce=1",
            allow_redirects=False,
            headers=self.headers,
        )

        # 删除请求头中的 Cookie
        self.headers.pop("cookie")

        # 如果请求返回的状态码不是 303，则登录失败
        if r.status != 303:
            raise AuthenticationError(message_translator("commands.cookies.FAILED"))

        await session.close()

        # 获取新 Cookie
        new_cookies = {"cookie": {}}
        for cookie in r.cookies.items():
            new_cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

        # 从响应 URI 中提取访问令牌和令牌 ID
        access_token, token_id = self._extract_tokens_from_uri(await r.text())

        # 获取资格令牌
        entitlements_token = await self.get_entitlements_token(access_token)

        return AuthCredentials(
            access_token=access_token,
            token_id=token_id,
            entitlements_token=entitlements_token,
            cookie=new_cookies,
        )

    async def refresh_token(self, cookies: Dict) -> AuthCredentials:
        """刷新访问令牌、权限令牌和Cookie。

        参数:
            cookies (Dict): 包含Cookie信息的字典。
        """

        data = await self.redeem_cookies(cookies)

        return AuthCredentials(
            access_token=data.access_token,
            entitlements_token=data.entitlements_token,
            cookie=data.cookie,
            expiry_token=data.expiry_token,
        )

    @staticmethod
    def _extract_tokens_from_response(data: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Extract tokens from data

        Args:
            data (Dict[str, Any]): A dictionary containing response data

        Returns:
            Tuple[str, str, str]: A tuple containing access_token, token_id, and expires_in

        """
        try:
            uri = data["response"]["parameters"]["uri"]
            pattern = re.compile(
                "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*"
                "id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*"
                "expires_in=(\d*)"
            )
            match = pattern.search(uri)
            if match is None:
                raise ValueError
            access_token, token_id, expires_in = match.groups()
            return access_token, token_id, expires_in
        except (IndexError, ValueError) as error:
            raise DataParseError("errors.DATA.PARSING_ERROR") from error

    @staticmethod
    def _extract_tokens_from_uri(uri: str) -> tuple[str, str]:
        """
        Extracts access token and ID token from a URL

        Args:
            uri (str): A URL string containing access token and ID token

        Returns:
            tuple: A tuple containing access token and ID token

        Raises:
            IndexError: If the URL is invalid, raises an IndexError

        """
        try:
            access_token = uri.split("access_token=")[1].split("&scope")[0]
            token_id = uri.split("id_token=")[1].split("&")[0]

            return access_token, token_id
        except IndexError as error:
            raise IndexError("Invalid uri") from error

    @staticmethod
    async def get_entitlements_token(access_token: str) -> Optional[str]:
        """
        用于获取权限令牌的静态方法

        Args:
            access_token (str): 访问令牌。

        Returns:
            Optional[str]: 权限令牌，如果不存在则返回 None。

        Raises:
            AuthenticationError: 如果无法从响应中提取所需的权限令牌。
        """

        session = ClientSession()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        try:
            async with session.post(
                "https://entitlements.auth.riotgames.com/api/token/v1",
                headers=headers,
                json={},
            ) as r:
                data = await r.json()
        except aiohttp.ClientResponseError as e:
            raise ResponseError(message_translator("errors.API.REQUEST_FAILED")) from e

        await session.close()
        try:
            return data["entitlements_token"]
        except KeyError as e:
            raise AuthenticationError(
                message_translator("errors.DATA.PARSING_ERROR")
            ) from e

    @staticmethod
    async def get_userinfo(access_token: str) -> Tuple[str, str, str]:
        """用于获取用户信息的静态方法。

        Args:
            access_token: 访问令牌。

        Returns:
            包含用户信息的元组，包括 PUUID、用户名和标签。

        Raises:
            AuthenticationError: 如果无法从响应中提取所需的用户信息。
        """

        session = ClientSession()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        async with session.post(
            "https://auth.riotgames.com/userinfo", headers=headers, json={}
        ) as r:
            data = await r.json()

        await session.close()

        try:
            puuid = data["sub"]
            name = data["acct"]["game_name"]
            tag = data["acct"]["tag_line"]
        except KeyError as e:
            raise AuthenticationError(
                message_translator("errors.AUTH.NO_NAME_TAG")
            ) from e
        else:
            return puuid, name, tag

    @staticmethod
    async def get_region(access_token: str, token_id: str) -> str:
        """用于获取区域的静态方法。

        Args:
            access_token: 访问令牌。
            token_id: 令牌 ID。

        Returns:
            区域字符串。

        Raises:
            AuthenticationError: 如果无法从响应中提取所需的区域信息。
        """

        session = ClientSession()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        body = {"id_token": token_id}

        async with session.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant",
            headers=headers,
            json=body,
        ) as r:
            data = await r.json()

        await session.close()

        try:
            region = data["affinities"]["live"]
        except KeyError as e:
            raise AuthenticationError(
                message_translator("errors.AUTH.UNSUPPORTED_REGION")
            ) from e
        else:
            return region

    @staticmethod
    async def token_validity(
        cookies: Dict, timestamp: int
    ) -> Optional[AuthCredentials]:
        """检查令牌是否有效。

        这个函数接受一个包含 Cookie 信息的字典，并验证其中的令牌是否有效。
        如果令牌有效，该函数将返回 True。如果令牌无效，该函数将尝试刷新令牌并返回更新后的 AuthCredentials。

        参数:
            cookies (Dict): 包含 Cookie 信息的字典。

        返回:
            Union[AuthCredentials, bool]: 如果令牌有效，返回 True；否则返回更新后的 AuthCredentials。

        异常:
            KeyError: 如果字典中缺少必要的键。

        用法:
            ```python
            result = await token_validity(cookies)
            if result is True:
                print("Token is valid.")
            else:
                print("Token is refreshed.", result)
            ```

        """
        if int(datetime.timestamp(datetime.now())) < timestamp:
            return None

        return await Auth().refresh_token(cookies)
