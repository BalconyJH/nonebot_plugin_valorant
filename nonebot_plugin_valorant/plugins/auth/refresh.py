from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12
from nonebot.params import ArgPlainText, T_State
from nonebot_plugin_saa import Image, Text, MessageFactory

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.database.models import User

from nonebot_plugin_valorant.utils.errors import DatabaseError
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

refresh = on_command("refresh", aliases={"刷新"}, priority=5, block=True)


@refresh.handle()
async def _(
        event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
        state: T_State,
):
    pass

@refresh.got("uid", prompt="请输入您的Riot用户名")
async def _(
        event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
        state: T_State,
        uid: str = ArgPlainText("uid"),
):
    if not id:
        msg_builder = MessageFactory(Text("刷nm呢"))
        await msg_builder.send()
        await refresh.finish()
    try:
        cache = await DB.get_user(event.user_id)
        await User.update(uid)
        msg_builder = MessageFactory(Text("刷新成功"))
        await msg_builder.send()
        await refresh.finish()
    except DatabaseError as e:
        msg_builder = MessageFactory(Text(f"刷新失败{e}"))
        await msg_builder.send()
        await refresh.finish()