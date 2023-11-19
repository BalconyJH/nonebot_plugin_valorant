from typing import Any

from nonebot.typing import T_State
from nonebot import logger, on_command
from nonebot.params import ArgPlainText
from nonebot_plugin_saa import Text, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils import user_login_status
from nonebot_plugin_valorant.utils.requestlib.auth import Auth
from nonebot_plugin_valorant.utils.errors import AuthenticationError

login = on_command("login", aliases={"登录"}, priority=5, block=True)
auth = Auth()

# async def cache_user_cookie(username: str, password: str) -> Optional[dict[str, Any]]:
#     return await auth.authenticate(username, password)

login.__doc__ = """用户登录"""


async def login_db(
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    result: dict[str, Any],
):
    if result["auth"] == "response":
        try:
            region = await auth.get_region(result["data"]["access_token"], result["data"]["token_id"])
            entitlements_token = await auth.get_entitlements_token(result["data"]["access_token"])
            puuid, name, tag = await auth.get_userinfo(result["data"]["access_token"])
            await DB.login(
                qq_uid=str(event.get_user_id()),
                username=f"{name}#{tag}",
                cookie=result["data"]["cookie"],
                access_token=result["data"]["access_token"],
                token_id=result["data"]["token_id"],
                expiry_token=result["data"]["expiry_token"],
                region=region,
                emt=entitlements_token,
                puuid=puuid,
            )
            logger.info(f"{name}#{tag}登录成功, QQ:{event.get_user_id()}")
            await login.finish(f"{name}#{tag}登录成功")
        except AuthenticationError as e:
            await login.finish(f"登录失败{e}")


@login.handle()
async def _(event: PrivateMessageEventV11 | PrivateMessageEventV12):
    if await user_login_status(str(event.get_user_id())) is True:
        await login.finish("您已登录,如需更换账号请先注销")


@login.got("username", prompt="请输入您的Riot用户名")
@login.got("password", prompt="请输入您的Riot密码")
async def _(
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    state: T_State,
    username: str = ArgPlainText("username"),
    password: str = ArgPlainText("password"),
):
    state["username"] = username
    state["password"] = password
    try:
        result = await auth.authenticate(username=state["username"], password=state["password"])
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
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    state: T_State,
    code: str = ArgPlainText("code"),
):
    try:
        state["result"] = await auth.auth_by_code(code, cookies=state["result"]["cookie"])
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
