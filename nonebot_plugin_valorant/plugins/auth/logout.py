import re
from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12
from nonebot.params import ArgPlainText, T_State
from nonebot_plugin_saa import Image, Text, MessageFactory

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.errors import DatabaseError
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

logout = on_command("logout", aliases={"登出"}, priority=5, block=True)
auth = Auth()


logout.handle()
logout.__doc__ = """用户注销"""


@logout.got("confirm", prompt="确定注销账户吗,确认请发送[是]或[yes]")
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
    confirm: str = ArgPlainText("confirm"),
):
    confirm = re.sub(r"[\[\]]", "", confirm)
    if confirm in ["是", "确定", "yes", "y"]:
        state["qq_uid"] = event.user_id
        try:
            await DB.logout(state["qq_uid"])
            msg_builder = MessageFactory(Text("注销成功"))
            await msg_builder.send()
            await logout.finish()
        except DatabaseError as e:
            msg_builder = MessageFactory(Text(f"注销失败{e}"))
            await msg_builder.send()
            await logout.finish()
    else:
        msg_builder = MessageFactory(Text("已取消"))
        await msg_builder.send()
        await logout.finish()
