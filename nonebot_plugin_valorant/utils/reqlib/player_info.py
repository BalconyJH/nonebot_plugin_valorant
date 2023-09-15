from typing import Tuple

from pydantic import BaseModel

from nonebot_plugin_valorant.utils.reqlib.auth import ClientSession
from nonebot_plugin_valorant.utils import AuthenticationError, message_translator


class PlayerInformation(BaseModel):
    puuid: str
    player_name: str
    region: str
    locale_code: str
    xp: str
    mmr: str
    wallet: dict[str, str]


class PlayerInfo:
    def __init__(self):
        # TODO document why this method is empty
        pass

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
