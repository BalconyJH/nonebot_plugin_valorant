import io
from pathlib import Path
from typing import Union

import requests
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
from nonebot_plugin_valorant.utils.render.storefront_skinpanel import parse_user_info

# require("nonebot_plugin_htmlrender")
# from nonebot_plugin_htmlrender import (
#     get_new_page,
# )  # noqa: E402

# html2pic = on_command("html2pic", aliases={"网页截图"}, priority=5, block=True)

# class SkinStore(BaseModel):


store = on_command("store", aliases={"商店"}, priority=5, block=True)
force_refresh = on_command(
    "force_refresh", aliases={"强制刷新"}, priority=5, block=True, permission=SUPERUSER
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
    print(data)
    from pathlib import Path

    template_path = str(Path(__file__).parent)
    template_name = "test.html"
    images = [
        {
            "src": f"./skins/{data.skin1.uuid}.png",
            "name": f"{data.skin1.name}",
            "cost": f"V{data.skin1.cost}",
        },
        {
            "src": f"./skins/{data.skin2.uuid}.png",
            "name": f"{data.skin2.name}",
            "cost": f"V{data.skin2.cost}",
        },
        {
            "src": f"./skins/{data.skin3.uuid}.png",
            "name": f"{data.skin3.name}",
            "cost": f"V{data.skin3.cost}",
        },
        {
            "src": f"./skins/{data.skin4.uuid}.png",
            "name": f"{data.skin4.name}",
            "cost": f"V{data.skin4.cost}",
        },
    ]
    # 设置模板
    # 模板中本地资源地址需要相对于 base_url 或使用绝对路径
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

    msg_builder = MessageFactory(Image(pic))
    await msg_builder.send()
    await store.finish()


@force_refresh.handle()
async def _force_refresh(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    print("force_refresh")
    # uuid = "43361d49-4331-ee30-e356-0f925e6e17b9"
    # user = await DB.get_user(str(event.user_id))
    # data = (await DB.get_skin(uuid)).names
    #
    # print(data, type(data))
    # print(repr(plugin_config.language_type))
    # print(plugin_config.language_type in data.keys())
    # print(data.get(plugin_config.language_type))
