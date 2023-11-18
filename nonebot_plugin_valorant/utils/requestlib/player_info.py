from pydantic import BaseModel


class PlayerWallet(BaseModel):
    valorant_points: int
    radiant_points: int
    kingdom_credits: int


class PlayerInformation(BaseModel):
    qq_uid: str | None = None
    puuid: str | None = None
    player_name: str | None = None
    region: str | None = None
    locale_code: str | None = "en-US"
    xp: str | None = None
    mmr: str | None = None
    wallet: PlayerWallet | None


# class PlayerInfo:
#     def __init__(self):
#         # TODO  有空再写
#         pass
#
#     @staticmethod
#     async def get_user_name(access_token: str) -> Tuple[str, str, str]:
#         """用于获取用户信息的静态方法。
#
#         Args:
#             access_token: 访问令牌。
#
#         Returns:
#             包含用户信息的元组，包括 PUUID、用户名和标签。
#
#         Raises:
#             AuthenticationError: 如果无法从响应中提取所需的用户信息。
#         """
#
#         session = ClientSession()
#
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {access_token}",
#         }
#
#         async with session.post(
#             "https://auth.riotgames.com/userinfo", headers=headers, json={}
#         ) as r:
#             data = await r.json()
#
#         await session.close()
#
#         try:
#             puuid = data["sub"]
#             name = data["acct"]["game_name"]
#             tag = data["acct"]["tag_line"]
#         except KeyError as e:
#             raise AuthenticationError(
#                 message_translator("errors.AUTH.NO_NAME_TAG")
#             ) from e
#         else:
#             return puuid, name, tag
