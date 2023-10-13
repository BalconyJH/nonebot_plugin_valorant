import copy
import time
from pathlib import Path

from rich import print
from nonebot import logger
from nonebot_plugin_htmlrender import template_to_pic

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.utils.requestlib.player_info import PlayerInformation

from ...database import DB
from ..errors import RequestError
from ..requestlib.endpoint import EndpointAPI
from ..requestlib.auth import Auth, AuthCredentials
from ..parsinglib.endpoint_parsing import SkinsPanel, skin_panel_parser


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
            print(resp)
            return await skin_panel_parser(resp)
        except RequestError as error:
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
        auth_info = copy.copy(data)
        resp = await EndpointAPI(player_info, auth_info).get_player_storefront()
        return await skin_panel_parser(resp)


async def render_skin_panel(data: SkinsPanel) -> bytes:
    print(data)
    start_time = time.time()
    template_path = str(Path(__file__).parent / "templates")
    template_name = "storefront_skinpanel.html"
    images = [
        {
            "src": f"{plugin_config.resource_path}\\{data.skin1.uuid}.png",
            "name": f"{data.skin1.name}",
            "cost": f"V{data.skin1.cost}",
        },
        {
            "src": f"{plugin_config.resource_path}\\{data.skin2.uuid}.png",
            "name": f"{data.skin2.name}",
            "cost": f"V{data.skin2.cost}",
        },
        {
            "src": f"{plugin_config.resource_path}\\{data.skin3.uuid}.png",
            "name": f"{data.skin3.name}",
            "cost": f"V{data.skin3.cost}",
        },
        {
            "src": f"{plugin_config.resource_path}\\{data.skin4.uuid}.png",
            "name": f"{data.skin4.name}",
            "cost": f"V{data.skin4.cost}",
        },
    ]
    pic = await template_to_pic(
        template_path=template_path,
        template_name=template_name,
        templates={"images": images},
        pages={
            "viewport": {"width": 600, "height": 700},
            "base_url": f"file://{template_path}",
        },
        wait=2,
    )
    logger.debug(f"渲染耗时: {time.time() - start_time}")
    return pic
