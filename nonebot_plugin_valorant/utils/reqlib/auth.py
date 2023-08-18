import json
import re
import ssl
from datetime import datetime, timedelta
from typing import Optional, Tuple, Any, Dict, Type

import aiohttp as aiohttp
import urllib3.exceptions
from pydantic import BaseModel, validator

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.utils.errors import AuthenticationError
from nonebot_plugin_valorant.utils.translator import Translator

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
message_translator = Translator().get_local_translation

PROXY = plugin_config.valorant_proxies


class Token(BaseModel):
    """
    A class representing authentication token for Valorant API.

    Attributes:
        access_token (str): The API access token.
        token_id (str): The ID of the token.
        expires_in (str): The duration in seconds for the token to expire.
        entitlements_token (str): The token for accessing entitlements.

    Raises:
        ValueError: If any of the required parameters is empty.

    """

    access_token: Optional[str]
    token_id: Optional[str]
    expires_in: Optional[str]
    entitlements_token: Optional[str]

    # noinspection PyMethodParameters
    @validator("access_token", "token_id", "expires_in", "entitlements_token")
    def check_token(cls, param):
        if param is None:
            raise ValueError(f"Param:{param} is empty")
        return param


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
        self._headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": Auth.RIOT_CLIENT_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
        }
        self.user_agent: str = Auth.RIOT_CLIENT_USER_AGENT

    @staticmethod
    def _extract_tokens(data: Dict[str, Any]) -> Type[Token]:
        """
        Extract tokens from data

        Args:
            data (Dict[str, Any]): A dictionary containing response data

        Returns:
            Tuple[str, str, str]: A tuple containing access_token, token_id, and expires_in

        """
        pattern = re.compile(
            "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*"
            "id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*"
            "expires_in=(\d*)"
        )
        Token.access_token, Token.token_id, Token.expires_in = pattern.findall(
            data["response"]["parameters"]["uri"]
        )[0]

        # 创建并返回Token对象
        return Token

    @staticmethod
    async def _extract_tokens_from_uri(url: str) -> Type[Token]:
        """
        Extracts access token and ID token from a URL

        Args:
            url (str): A URL string containing access token and ID token

        Returns:
            tuple: A tuple containing access token and ID token

        Raises:
            IndexError: If the URL is invalid, raises an IndexError

        """
        try:
            Token.access_token = url.split("access_token=")[1].split("&scope")[0]
            Token.token_id = url.split("id_token=")[1].split("&")[0]

            return Token
        except IndexError as error:
            raise IndexError("Invalid uri") from error

    async def authenticate(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """用于认证用户的函数。

        Args:
            username: 要认证的用户名。
            password: 要认证的密码。

        Returns:
            如果认证成功，则返回包含认证数据的字典，包括 cookie、访问令牌和令牌 ID。如果认证需要 2FA，则此函数
            返回一个包含 cookie 数据和提示用户输入 2FA 代码的消息的字典。否则，此函数返回 None。

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
            headers=self._headers,
            proxy=PROXY,
        )

        # 准备授权请求的 cookies。
        cookies = {"cookie": {}}
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
            headers=self._headers,
            cookies=cookies["cookie"],
            proxy=PROXY,
        ) as response:
            data = await response.json()
            print(data)
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
            response = self._extract_tokens(data)
            access_token = response.access_token
            token_id = response.token_id

            # 设置令牌的到期时间。
            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies["expiry_token"] = int(datetime.timestamp(expiry_token))

            # 返回认证数据。
            return {
                "auth": "response",
                "data": {
                    "cookie": cookies,
                    "access_token": access_token,
                    "token_id": token_id,
                },
            }
        elif data["type"] == "multifactor":
            if response.status == 429:
                # 如果用户发送了太多请求，请引发 AuthenticationError。
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

    @staticmethod
    async def get_entitlements_token(access_token: str) -> Optional[str]:
        """
        用于获取权限令牌的静态方法。

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

        async with session.post(
            "https://entitlements.auth.riotgames.com/api/token/v1",
            headers=headers,
            json={},
        ) as r:
            data = await r.json()

        await session.close()
        try:
            entitlements_token = data["entitlements_token"]
        except KeyError as e:
            raise AuthenticationError(
                message_translator("errors.AUTH.COOKIES_EXPIRED")
            ) from e
        else:
            return entitlements_token

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
        except KeyError:
            raise AuthenticationError(
                message_translator("errors.AUTH.NO_NAME_TAG")
            )
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
        except KeyError:
            raise AuthenticationError(
                message_translator("errors.AUTH.UNSUPPORTED_REGION")
            )
        else:
            return region

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
        data = {"type": "multifactor", "code": code, "rememberDevice": True}

        # 发送输入 2FA 验证码请求。
        async with session.put(
            self.AUTH_URL,
            headers=self._headers,
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
            extract_tokens = await self._extract_tokens_from_uri(uri)

            return {
                "auth": "response",
                "data": {
                    "cookie": cookies,
                    "access_token": extract_tokens.access_token,
                    "token_id": extract_tokens.token_id,
                },
            }
        raise AuthenticationError(
            message_translator("errors.AUTH.2FA_INVALID_CODE")
        )

    async def redeem_cookies(self, cookies: Dict) -> dict[str, str | None | dict[str, dict[Any, Any]]]:
        """
        该函数用于兑换 cookies。

        Args:
            cookies: 包含 cookies 的字典。

        Returns:
            一个元组，包含兑换后的 cookies，access token 和 entitlements token。

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

        extract_tokens = await self._extract_tokens_from_uri(data)
        entitlements_token = await self.get_entitlements_token(extract_tokens.access_token)

        return {
            "cookies": new_cookies,
            "access_token": extract_tokens.access_token,
            "entitlements_token": entitlements_token,
        }

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

    async def login_with_cookie(self, cookies: Dict) -> Dict[str, Any]:
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
        self._headers["cookie"] = cookie_payload

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
            headers=self._headers,
        )

        # 删除请求头中的 Cookie
        self._headers.pop("cookie")

        # 如果请求返回的状态码不是 303，则登录失败
        if r.status != 303:
            raise AuthenticationError(message_translator("commands.cookies.FAILED"))

        await session.close()

        # 获取新 Cookie
        new_cookies = {"cookie": {}}
        for cookie in r.cookies.items():
            new_cookies["cookie"][cookie[0]] = str(cookie).split("=")[1].split(";")[0]

        # 从响应 URI 中提取访问令牌和令牌 ID
        access_token, token_id = await self._extract_tokens_from_uri(await r.text())

        # 获取资格令牌
        entitlements_token = await self.get_entitlements_token(access_token)

        return {
            "cookies": new_cookies,
            "AccessToken": access_token,
            "token_id": token_id,
            "emt": entitlements_token,
        }

    async def refresh_token(
        self, cookies: Dict
    ) -> Tuple[Tuple[str, Dict], Tuple[str, Dict], Tuple[str, Dict]]:
        """刷新访问令牌、权限令牌和Cookie。

        参数:
            cookies (Dict): 包含Cookie信息的字典。

        返回:
            Tuple[Tuple[str, Dict], Tuple[str, Dict], Tuple[str, Dict]]: 包含三个元组的元组。
                第一个元组包含访问令牌作为第一个元素，字典作为第二个元素。
                第二个元组包含权限令牌作为第一个元素，字典作为第二个元素。
                第三个元组包含Cookie作为第一个元素，字典作为第二个元素。
        """

        data = await self.redeem_cookies(cookies)
        access_token = data["access_token"]
        entitlements_token = data["entitlements_token"]
        cookies = data["cookies"]

        return access_token, entitlements_token, cookies
