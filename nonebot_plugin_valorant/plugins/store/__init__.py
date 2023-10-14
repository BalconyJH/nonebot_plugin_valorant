import io
import time
import asyncio
from pathlib import Path
from typing import Union

import requests
from rich import print
from nonebot import on_command
from pydantic import BaseModel
from viztracer import VizTracer
from nonebot.params import T_State
from nonebot.permission import SUPERUSER
from nonebot_plugin_htmlrender import template_to_pic
from nonebot_plugin_saa import Text, Image, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11

# from nonebot.adapters.onebot.v12 import Bot, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant import plugin_config
from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.requestlib.auth import Auth
from nonebot_plugin_valorant.utils.translator import Translator
from nonebot_plugin_valorant.resources.image.skin import download_images_from_db
from nonebot_plugin_valorant.utils import AuthenticationError, user_login_status
from nonebot_plugin_valorant.utils.parsinglib.endpoint_parsing import SkinsPanel
from nonebot_plugin_valorant.utils.requestlib.player_info import PlayerInformation
from nonebot_plugin_valorant.utils.render.storefront_skinpanel import (
    parse_user_info,
    render_skin_panel,
)

# require("nonebot_plugin_htmlrender")
# from nonebot_plugin_htmlrender import (
#     get_new_page,
# )  # noqa: E402

# html2pic = on_command("html2pic", aliases={"网页截图"}, priority=5, block=True)

# class SkinStore(BaseModel):


store = on_command("store", aliases={"商店"}, priority=5, block=True)
test = on_command("test", aliases={"test"}, priority=5, block=True)
auth = Auth()


store.handle()
store.__doc__ = """商店"""


async def cache_skins_store_into_db(
    user_data: PlayerInformation, skin_data: SkinsPanel
) -> None:
    """缓存商店皮肤信息到数据库"""
    await DB.cache_player_skins_store(
        uuid=user_data.puuid,
        offer_1=skin_data.skin1.dict(),
        offer_2=skin_data.skin2.dict(),
        offer_3=skin_data.skin3.dict(),
        offer_4=skin_data.skin4.dict(),
        duration=skin_data.duration,
    )


@store.handle()
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    # tracer = VizTracer()
    # tracer.start()
    try:
        skin_data, player_info = await parse_user_info(event.user_id)
        await cache_skins_store_into_db(player_info, skin_data)
        pic = await render_skin_panel(skin_data)
        msg_builder = MessageFactory(Image(pic))
        await msg_builder.send()
        await store.finish()
    except AuthenticationError as e:
        await store.finish(f"登录信息失效{e},  请重新使用[/login]登录")
    # tracer.stop()
    # tracer.save("test.html")


@test.handle()
async def _test(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    await download_images_from_db()
