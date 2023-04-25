from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent, Message
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import Arg
from nonebot.params import ArgPlainText, T_State
# from nonebot_plugin_valorant.database.temporary_db import add_user
from nonebot_plugin_valorant.utils.errors import AuthenticationError

from ...utils import (on_command)
from nonebot_plugin_valorant.utils.auth import Auth

login = on_command("login", priority=5, block=True)
auth = Auth()


@login.got("username", prompt="请输入您的Riot用户名")
async def _(event: PrivateMessageEvent,
            state: T_State,
            username: str = ArgPlainText('username')):
    state["username"] = username


@login.got("password", prompt="请输入您的Riot密码")
async def _(event: PrivateMessageEvent,
            state: T_State,
            password: str = ArgPlainText('password')):
    state["password"] = password
    try:
        result = await auth.authenticate(state["username"], state["password"])
        state["result"] = result
        print(state["result"])
    except AuthenticationError as e:
        await login.reject(f"{e}")


@login.got("2fa", prompt="请输入您的2FA验证码")
async def _(event: PrivateMessageEvent,
            state: T_State,
            code: str = ArgPlainText('2fa')):
    state["code"] = code
    print("1")