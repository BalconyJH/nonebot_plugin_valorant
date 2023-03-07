import re
import ssl
from typing import Optional, Tuple, Any, Dict
from datetime import datetime, timedelta

import aiohttp as aiohttp
import urllib3.exceptions
from .errors import AuthenticationError

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile(r'access_token=([\w.-]*)&id_token=([\w.-]*)&expires_in=(\d*)')
    return pattern.findall(data['response']['parameters']['uri'])[0]


def _extract_tokens_from_uri(url: str) -> Optional[Tuple[str, Any]]:
    try:
        access_token = url.split("access_token=")[1].split("&scope")[0]
        token_id = url.split("id_token=")[1].split("&")[0]
        return access_token, token_id
    except IndexError as e:
        raise IndexError('Cookies Invalid') from e


# https://developers.cloudflare.com/ssl/ssl-tls/cipher-suites/

FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA',
    'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-ECDSA-AES128-SHA',
    'ECDHE-ECDSA-AES256-SHA',
    'ECDHE+AES128',
    'ECDHE+AES256',
    'ECDHE+3DES',
    'RSA+AES128',
    'RSA+AES256',
    'RSA+3DES',
]


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        super().__init__(*args, **kwargs, cookie_jar=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(ssl=ctx))


class Auth:
    RIOT_CLIENT_USER_AGENT = "RiotClient/60.0.6.4770705.4749685 rso-auth (Windows;10;;Professional, x64)"

    def __init__(self) -> None:
        self._headers: Dict = {
            'Content-Type': 'application/json',
            'User-Agent': Auth.RIOT_CLIENT_USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
        }
        self.user_agent = Auth.RIOT_CLIENT_USER_AGENT

    async def aauthenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """This function is used to authenticate the user."""

        session = ClientSession()

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        response = await session.post('https://auth.riotgames.com/api/v1/authorization',
                                      json=data, headers=self._headers)

        # prepare cookies for auth request
        cookies = {'cookie': {}}
        for cookie in response.cookies.items():
            cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        data = {"type": "auth", "username": username, "password": password, "remember": True}

        async with session.post('https://auth.riotgames.com/api/v1/authorization',
                                json=data, headers=self._headers, cookies=cookies['cookie']) as response:
            data = await response.json()
            for cookie in response.cookies.items():
                cookies['cookie'][cookie[0]] = str(cookie).split('=')[1].split(';')[0]

        await session.close()

        if data['type'] == 'response':
            response = _extract_tokens(data)
            access_token = response[0]
            token_id = response[1]

            expiry_token = datetime.now() + timedelta(minutes=59)
            cookies['expiry_token'] = int(datetime.timestamp(expiry_token))

            return {'auth': 'response', 'data': {'cookie': cookies, 'access_token': access_token, 'token_id': token_id}}

        elif data['type'] == 'multifactor':

            if response.status == 429:
                raise AuthenticationError("RATELIMIT, Please wait a few minutes and try again.")

            label_modal = local_response.get('INPUT_2FA_CODE')
            WaitFor2FA = {"auth": "2fa", "cookie": cookies, 'label': label_modal}

            if data['multifactor']['method'] == 'email':
                WaitFor2FA[
                    'message'
                ] = f"{local_response.get('2FA_TO_EMAIL', 'Riot sent a code to')} {data['multifactor']['email']}"
                return WaitFor2FA

            WaitFor2FA['message'] = local_response.get('2FA_ENABLE', 'You have 2FA enabled!')
            return WaitFor2FA

        raise AuthenticationError(local_response.get('INVALID_PASSWORD', 'Your username or password may be incorrect!'))
