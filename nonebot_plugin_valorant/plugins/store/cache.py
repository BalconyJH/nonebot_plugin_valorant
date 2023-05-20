from contextlib import suppress

from nonebot import require
from nonebot.log import logger

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils.errors import ResponseError
from nonebot_plugin_valorant.utils.reqlib.client import get_manifest_id
from nonebot_plugin_valorant.utils.reqlib.request_res import get_skin, get_tier

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler


async def cache_store():
    skin = await get_skin()
    await DB.cache_skin(skin)
    tire = await get_tier()
    await DB.cache_tier(tire)
    logger.info("皮肤缓存完成")


async def cache_manifest_id():
    return await DB.get_version("manifest_id")


@scheduler.scheduled_job("cron", hour="*/1", id="refresh_store")
async def refresh_store():
    """
    比对资源清单值判断缓存时效性

    """
    db_cache = await cache_manifest_id()
    manifest_id = await get_manifest_id()
    if db_cache != manifest_id:
        await cache_store()
        await DB.update_version("manifest_id", manifest_id=manifest_id)
        with suppress(ResponseError):
            await cache_store()
