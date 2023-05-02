from typing import Any, Optional

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, Message
from nonebot.params import ArgPlainText, T_State, CommandArg

from nonebot_plugin_valorant.utils.auth import Auth
from nonebot_plugin_valorant.database.temporary_db import add_user
from nonebot_plugin_valorant.utils.errors import AuthenticationError
from nonebot_plugin_valorant.utils.translator import message_translator

login = on_command("login", aliases={"登录"}, priority=5, block=True)
auth = Auth()


# async def cache_user_cookie(username: str, password: str) -> Optional[dict[str, Any]]:
#     return await auth.authenticate(username, password)


@login.got("username", prompt="请输入您的Riot用户名")
@login.got("password", prompt="请输入您的Riot密码")
async def _(event: PrivateMessageEvent,
            state: T_State,
            username: str = ArgPlainText("username"),
            password: str = ArgPlainText("password")):
    state["username"] = username
    state["password"] = password
    try:
        result = await auth.authenticate(username=state["username"], password=state["password"])
        state["result"] = result
        if result == "None":
            login.finish("连接错误")

    except AuthenticationError as e:
        await login.reject(f"{e}")


@login.handle()
async def _(bot, event: PrivateMessageEvent, state: T_State):
    if state["result"]["auth"] == "2fa":
        print(state["result"])
        login.skip()
    elif state["result"]["auth"] == "response":
        await login.finish("登录成功")


@login.got("code", prompt="请输入您的2FA验证码")
async def _(bot, event: PrivateMessageEvent, state: T_State, code: str = ArgPlainText("code")):
    try:
        result = await auth.auth_by_code(code, cookies=state["result"]["cookie"])
        state["result"] = result
        if result == "None":
            login.finish("连接错误")
    except AuthenticationError as e:
        await login.reject(f"{e}")
