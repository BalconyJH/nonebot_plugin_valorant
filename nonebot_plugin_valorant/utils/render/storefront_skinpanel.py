import copy

from ...database import DB
from ..errors import RequestError
from ..requestlib.endpoint import EndpointAPI
from ..requestlib.auth import Auth, AuthCredentials
from ..requestlib.player_info import PlayerInformation
from ..parsinglib.endpoint_parsing import skin_panel_parser


async def login_status(qq_uid: str) -> bool:
    return await DB.get_user(qq_uid) is not None


async def parse_user_info(qq_uid: str):
    user = await DB.get_user(qq_uid)
    player_info = PlayerInformation(
        puuid=user.puuid,
        player_name=user.username,
        region=user.region,
    )
    auth_info = AuthCredentials(
        cookie=user.cookie,
        access_token=user.access_token,
        entitlements_token=user.emt,
        expiry_token=user.expiry_token,
    )
    data = await Auth.token_validity(auth_info.cookie, auth_info.expiry_token)
    if data is None:
        print("token有效")
        try:
            resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
            return await skin_panel_parser(resp)
        except RequestError as error:
            print(error)
            data = await Auth().redeem_cookies(auth_info.cookie)
            resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
            await DB.update_user(
                filter_by={"qq_uid": qq_uid},
                update_values={
                    "access_token": data.access_token,
                    "token_id": data.token_id,
                    "expiry_token": data.expiry_token,
                    "emt": data.entitlements_token,
                    "cookie": data.cookie,
                },
            )
            return await skin_panel_parser(resp)
    else:
        print("token无效")
        await DB.update_user(
            filter_by={"qq_uid": qq_uid},
            update_values={
                "access_token": data.access_token,
                "token_id": data.token_id,
                "expiry_token": data.expiry_token,
                "emt": data.entitlements_token,
                "cookie": data.cookie,
            },
        )
        print(data.expiry_token)
        auth_info = copy.copy(data)
        resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
        return await skin_panel_parser(resp)
