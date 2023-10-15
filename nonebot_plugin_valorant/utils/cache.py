from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils.requestlib.client import get_version
from nonebot_plugin_valorant.utils.requestlib.request_res import get_skin, get_tier


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
    await DB.init_version(
        filter_by={"manifestId": data.get("manifestId")}, update_value={"initial": True}
    )


async def init_cache():
    await cache_store()
    await cache_version()
