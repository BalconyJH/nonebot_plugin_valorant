from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.params import ArgPlainText, T_State

from nonebot_plugin_valorant.utils.reqlib.auth import Auth

store = on_command("store", aliases={"商店"}, priority=5, block=True)
auth = Auth()


store.handle()
store.__doc__ = """商店"""


@store.handle()
async def _(
        event: PrivateMessageEvent,
        state: T_State,
        confirm: str = ArgPlainText("confirm"),
):
    endpoint =