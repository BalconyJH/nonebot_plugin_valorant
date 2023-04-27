from typing import Any, Optional

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message
from nonebot.params import ArgPlainText, T_State, CommandArg

from nonebot_plugin_valorant.utils.auth import Auth
# from nonebot_plugin_valorant.database.temporary_db import add_user
from nonebot_plugin_valorant.utils.errors import AuthenticationError
from nonebot_plugin_valorant.utils.translator import message_translator

login = on_command("login", aliases={"登录"}, priority=5, block=True)
auth = Auth()


async def cache_user_cookie(username: str, password: str) -> Optional[dict[str, Any]]:
    return await auth.authenticate(username, password)


@login.handle()
async def login_handle_function(args: Message = CommandArg()):
    # TODO document why this method is empty
    pass


@login.got("username", prompt="请输入您的Riot用户名")
@login.got("password", prompt="请输入您的Riot密码")
async def _(event: PrivateMessageEvent,
            state: T_State,
            username: str = ArgPlainText("username"),
            password: str = ArgPlainText("password")):
    state["username"] = username
    state["password"] = password
    try:
        result = await cache_user_cookie(username=state["username"], password=state["password"])
        if result is None:
            raise AuthenticationError(message_translator("请求错误,请重试"))

    except AuthenticationError as e:
        await login.reject(f"{e}")


@login.got("2fa", prompt="请输入您的2FA验证码")
async def _(event: PrivateMessageEvent,
            state: T_State,
            code: str = ArgPlainText('2fa')):
    state["code"] = code
    print("1")
