import json
from contextlib import suppress
from typing import Dict, Any, Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12
from nonebot.params import ArgPlainText, T_State
from nonebot_plugin_saa import Image, Text, MessageFactory


from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.errors import AuthenticationError
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

login = on_command("login", aliases={"登录"}, priority=5, block=True)
auth = Auth()

# async def cache_user_cookie(username: str, password: str) -> Optional[dict[str, Any]]:
#     return await auth.authenticate(username, password)

login.handle()
login.__doc__ = """用户登录"""


async def login_db(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    result: Dict[str, Any],
):
    if result["auth"] == "response":
        with suppress(AuthenticationError):
            region = await auth.get_region(
                result["data"]["access_token"], result["data"]["token_id"]
            )
            entitlements_token = await auth.get_entitlements_token(
                result["data"]["access_token"]
            )
            puuid, name, tag = await auth.get_userinfo(result["data"]["access_token"])
            player_name = f"{name}#{tag}" if tag and tag is not None else "no_username"
        await DB.login(
            qq_uid=str(event.user_id),
            username=player_name,
            cookie=json.dumps(result["data"]["cookie"]),
            access_token=result["data"]["access_token"],
            token_id=result["data"]["token_id"],
            region=region,
            emt=entitlements_token,
            puuid=puuid,
        )
        await login.finish("登录成功")


async def check_user(event: Union[PrivateMessageEventV11, PrivateMessageEventV12]):
    if await DB.get_user(str(event.user_id)) is not None:
        await login.finish("您已登录,如需更换账号请先注销")


@login.handle()
async def _(event: Union[PrivateMessageEventV11, PrivateMessageEventV12]):
    await check_user(event)


@login.got("username", prompt="请输入您的Riot用户名")
@login.got("password", prompt="请输入您的Riot密码")
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
    username: str = ArgPlainText("username"),
    password: str = ArgPlainText("password"),
):
    state["username"] = username
    state["password"] = password
    try:
        result = await auth.authenticate(
            username=state["username"], password=state["password"]
        )
        state["result"] = result
        if result == "None":
            msg_builder = MessageFactory(Text("未知错误"))
            await msg_builder.send()
            await login.finish()
    except AuthenticationError as e:
        msg_builder = MessageFactory(Text(f"登陆失败{e}"))
        await msg_builder.send()
        await login.finish()
    if state["result"]["auth"] == "2fa":
        login.skip()
    elif state["result"]["auth"] == "response":
        await login_db(event, state["result"])
        msg_builder = MessageFactory(Text("登陆成功"))
        await msg_builder.send()
        await login.finish()


@login.got("code", prompt="请输入您的2FA验证码")
async def _(
    event: Union[PrivateMessageEventV11, PrivateMessageEventV12],
    state: T_State,
    code: str = ArgPlainText("code"),
):
    try:
        state["result"] = await auth.auth_by_code(
            code, cookies=state["result"]["cookie"]
        )
        if state["result"] == "None":
            msg_builder = MessageFactory(Text("未知错误"))
            await msg_builder.send()
            await login.finish()
        elif state["result"]["auth"] == "response":
            await login_db(event, state["result"])
            msg_builder = MessageFactory(Text("登陆成功"))
            await msg_builder.send()
            await login.finish()
    except AuthenticationError as e:
        msg_builder = MessageFactory(Text(f"登陆失败{e}"))
        await msg_builder.send()
        await login.finish()
