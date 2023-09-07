from nonebot import logger

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils.reqlib.request_res import get_skin, get_tier
from nonebot_plugin_valorant.utils.reqlib.client import (
    get_version,
    get_manifest_id,
    get_version_data,
)


async def cache_store():
    """
    缓存商店数据
    Returns:
        None

    """
    await DB.cache_skin(await get_skin())
    await DB.cache_tier(await get_tier())


async def cache_version():
    """
    缓存版本信息
    Returns:
        None

    """
    data = await get_version()
    await DB.update_version(**data)


async def init_cache():
    await cache_store()
    await cache_version()
