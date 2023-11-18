from contextlib import suppress

from nonebot import require

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils import ResponseError
from nonebot_plugin_valorant.utils.cache import cache_store
from nonebot_plugin_valorant.utils.requestlib.client import get_manifest_id

require("nonebot_plugin_apscheduler")


async def refresh_store():
    """
    比对资源清单值判断缓存时效性

    """
    manifest_id = get_manifest_id()
    db_cache = await DB.get_version("manifestId")
    if db_cache[0] != manifest_id:
        await cache_store()
        await DB.update_version()
        with suppress(ResponseError):
            await cache_store()
