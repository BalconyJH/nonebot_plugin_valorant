import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.params import ArgPlainText, T_State

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.errors import DatabaseError
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

logout = on_command("logout", aliases={"登出"}, priority=5, block=True)
auth = Auth()


logout.handle()
logout.__doc__ = """用户注销"""


@logout.got("confirm", prompt="确定注销账户吗,确认请发送[是]或[yes]")
async def _(
    event: PrivateMessageEvent,
    state: T_State,
    confirm: str = ArgPlainText("confirm"),
):
    confirm = re.sub(r"[\[\]]", "", confirm)
    if confirm in ["是", "确定", "yes", "y"]:
        state["qq_uid"] = event.user_id
        try:
            await DB.logout(state["qq_uid"])
            await logout.finish("注销成功")
        except Exception as e:
            raise DatabaseError("删除失败,请联系管理员") from e
