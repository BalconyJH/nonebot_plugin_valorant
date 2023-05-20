from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import ArgPlainText, T_State
from nonebot.permission import SUPERUSER

from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

store = on_command("store", aliases={"商店"}, priority=5, block=True)
force_refresh = on_command("force_refresh", aliases={"强制刷新"}, priority=5, block=True, permission=SUPERUSER)
auth = Auth()

store.handle()
store.__doc__ = """商店"""


@store.handle()
async def _(
        event: PrivateMessageEvent,
        state: T_State,
        confirm: str = ArgPlainText("confirm"),
):
    endpoint = "test"


@force_refresh.handle()
async def _force_refresh(
        event: PrivateMessageEvent,
        state: T_State,
):
    try:
        await cache_store()
        await force_refresh.finish("刷新成功")
    except FinishedException:
        pass
    except Exception as e:
        await force_refresh.finish(f"刷新失败{e}")
        logger.warning(f"刷新失败{e}")
