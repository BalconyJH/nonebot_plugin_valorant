from ...database import DB
from ..errors import RequestError
from ..requestlib.endpoint import EndpointAPI
from ..requestlib.auth import Auth, AuthCredentials
from ..requestlib.player_info import PlayerInformation
from ..parsinglib.endpoint_parsing import parse_raw_data


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
        try:
            resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
            return await parse_raw_data(resp)
        except RequestError as error:
            data = await Auth().redeem_cookies(auth_info.cookie)
            resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
            await DB.update_user(
                qq_uid=qq_uid,
                access_token=data.access_token,
                token_id=data.token_id,
                expiry_token=data.expiry_token,
                emt=data.entitlements_token,
                cookie=data.cookie,
            )
            return await parse_raw_data(resp)
    else:
        await DB.update_user(
            qq_uid=qq_uid,
            access_token=data.access_token,
            token_id=data.token_id,
            expiry_token=data.expiry_token,
            emt=data.entitlements_token,
            cookie=data.cookie,
        )
        auth_info.access_token = data.access_token
        auth_info.token_id = data.token_id
        auth_info.expiry_token = data.expiry_token
        auth_info.entitlements_token = data.entitlements_token
        auth_info.cookie = data.cookie
        resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
        return await parse_raw_data(resp)
