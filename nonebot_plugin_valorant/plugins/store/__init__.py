import io
import time
from pathlib import Path
from typing import Union

import requests
from rich import print
from nonebot import on_command
from pydantic import BaseModel
from nonebot.params import T_State
from nonebot.permission import SUPERUSER
from nonebot_plugin_htmlrender import template_to_pic
from nonebot_plugin_saa import Text, Image, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11

# from nonebot.adapters.onebot.v12 import Bot, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant import plugin_config
from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils import user_login_status
from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.requestlib.auth import Auth
from nonebot_plugin_valorant.utils.translator import Translator
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
test = on_command(
    "force_refresh", aliases={"test"}, priority=5, block=True, permission=SUPERUSER
)
auth = Auth()


store.handle()
store.__doc__ = """商店"""


@store.handle()
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    data = await parse_user_info(event.user_id)
    pic = await render_skin_panel(data)
    msg_builder = MessageFactory(Image(pic))
    await msg_builder.send()
    await store.finish()


@test.handle()
async def _force_refresh(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    pass
