import json
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.params import ArgPlainText, T_State
from sqlalchemy.exc import IntegrityError

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.errors import AuthenticationError
from ...utils.reqlib.auth import Auth

login = on_command("auth", aliases={"登录"}, priority=5, block=True)
auth = Auth()

# async def cache_user_cookie(username: str, password: str) -> Optional[dict[str, Any]]:
#     return await auth.authenticate(username, password)

login.handle()
login.__doc__ = """用户登录"""


async def login_db(
    event: PrivateMessageEvent,
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
            expiry_token = datetime.timestamp(
                datetime.now(timezone.utc) + timedelta(minutes=59)
            )
            puuid, name, tag = await auth.get_userinfo(result["data"]["access_token"])
            player_name = f"{name}#{tag}" if tag and tag is not None else "no_username"
        await DB.login(
            qq_uid=event.user_id,
            username=player_name,
            cookie=json.dumps(result["data"]["cookie"]),  # cookie is a dict
            access_token=result["data"]["access_token"],
            token_id=result["data"]["token_id"],
            region=region,
            emt=entitlements_token,
            puuid=puuid,
            expiry_token=expiry_token,
        )
        await login.finish("登录成功")


@login.got("username", prompt="请输入您的Riot用户名")
@login.got("password", prompt="请输入您的Riot密码")
async def _(
    event: PrivateMessageEvent,
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
        print(result)
        if result == "None":
            login.finish("未知错误")
    except AuthenticationError as e:
        await login.finish(f"{e}")
    if state["result"]["auth"] == "2fa":
        login.skip()
    elif state["result"]["auth"] == "response":
        try:
            await login_db(event, state["result"])
        except IntegrityError:
            await login.finish("目前一个QQ仅支持登录一个账号")


@login.got("code", prompt="请输入您的2FA验证码")
async def _(
    event: PrivateMessageEvent, state: T_State, code: str = ArgPlainText("code")
):
    try:
        state["result"] = await auth.auth_by_code(
            code, cookies=state["result"]["cookie"]
        )
        print(state["result"])
        if state["result"] == "None":
            login.finish("未知错误")
        elif state["result"]["auth"] == "response":
            print(state["result"]["auth"])
            await login_db(event, state["result"])
    except AuthenticationError as e:
        await login.finish(f"登陆失败{e}")
        raise AuthenticationError("登陆失败") from e
    except IntegrityError:
        await login.finish("目前一个QQ仅支持登录一个账号")
