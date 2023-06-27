from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12
from nonebot.adapters.kaiheila import MessageSegment
from nonebot_plugin_saa import Image, Text, MessageFactory
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import ArgPlainText, T_State
from nonebot.permission import SUPERUSER

from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

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
    confirm: str = ArgPlainText("confirm"),
):
    endpoint = "test"


@force_refresh.handle()
async def _force_refresh(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
):
    try:
        await cache_store()
        msg_builder = MessageFactory(Text("刷新成功"))
    except Exception as err:
        msg_builder = MessageFactory(Text(f"刷新失败{err}"))
        logger.warning(f"刷新失败{err}")
    await msg_builder.send()
    await msg_builder.finish()