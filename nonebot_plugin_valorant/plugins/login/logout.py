from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.params import ArgPlainText, T_State, CommandArg

from nonebot_plugin_valorant.utils.reqlib.auth import Auth
from nonebot_plugin_valorant.utils.errors import AuthenticationError, DatabaseError
from nonebot_plugin_valorant.database.temporary_db import delete_user

logout = on_command("logout", aliases={"登出"}, priority=5, block=True)
auth = Auth()


logout.handle()
logout.__doc__ = """用户注销"""


@logout.got("username", prompt="请输入您的Riot用户名")
async def _(
    event: PrivateMessageEvent,
    state: T_State,
    username: str = ArgPlainText("username"),
    password: str = ArgPlainText("password"),
):
    state["username"] = username
    state["qq_uid"] = event.user_id
    try:
        delete_user(state["qq_uid"], state["username"])
        await logout.finish("注销成功")
    except Exception as e:
        raise DatabaseError("删除失败,请联系管理员") from e
