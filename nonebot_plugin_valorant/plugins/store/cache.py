from contextlib import suppress

from nonebot import require

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils import cache_store
from nonebot_plugin_valorant.utils.errors import ResponseError
from nonebot_plugin_valorant.utils.reqlib.client import get_manifest_id, get_version

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler


@scheduler.scheduled_job("cron", hour="*/1", id="refresh_store")
async def refresh_store():
    """
    比对资源清单值判断缓存时效性

    """
    db_cache = await DB.get_version("manifest_id")
    manifest_id = await get_manifest_id()
    if db_cache != manifest_id:
        await cache_store()
        await DB.update_version()
        with suppress(ResponseError):
            await cache_store()
