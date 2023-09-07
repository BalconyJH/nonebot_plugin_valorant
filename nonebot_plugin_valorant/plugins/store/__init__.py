from typing import Union

from nonebot import on_command
from pydantic import BaseModel
from nonebot.params import T_State
from nonebot.permission import SUPERUSER
from nonebot_plugin_saa import Text, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11

# from nonebot.adapters.onebot.v12 import Bot, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant.utils.reqlib.auth import Auth
from nonebot_plugin_valorant.utils import user_login_status
from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.translator import Translator

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
message_translator = Translator().get_local_translation


store.handle()
store.__doc__ = """商店"""


@store.handle()
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    if await user_login_status(str(event.user_id)) is None:
        await store.finish("请先登录")
    else:
        await store.finish("商店功能暂未开放")


@force_refresh.handle()
async def _force_refresh(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    # try:
    await cache_store()
    msg_builder = MessageFactory(Text("刷新成功"))


# @html2pic.handle()
# async def _html2pic(bot: Bot, event: MessageEvent):
#     from pathlib import Path
#
#     # html 可使用本地资源
#     async with get_new_page(viewport={"width": 300, "height": 300}) as page:
#         await page.goto(
#             "file://" + (str(Path(__file__).parent / "html2pic.html")),
#             wait_until="networkidle",
#             )
#         pic = await page.screenshot(full_page=True, path="./html2pic.png")
#
#     await html2pic.finish(MessageSegment.image(pic))
