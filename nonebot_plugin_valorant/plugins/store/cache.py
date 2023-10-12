from contextlib import suppress

from nonebot import require, on_command
from nonebot.params import T_State, ArgPlainText
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Text, Image, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils import cache_store
from nonebot_plugin_valorant.utils.errors import ResponseError
from nonebot_plugin_valorant.utils.requestlib.client import get_manifest_id

require("nonebot_plugin_apscheduler")


@scheduler.scheduled_job("cron", hour="*/1", id="refresh_store")
async def refresh_store():
    """
    比对资源清单值判断缓存时效性

    """
    db_cache = await DB.get_version()
    manifest_id = await get_manifest_id()
    if db_cache != manifest_id:
        await cache_store()
        await DB.update_version()
        with suppress(ResponseError):
            await cache_store()
