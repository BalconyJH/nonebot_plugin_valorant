from nonebot.log import logger

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.utils.reqlib.request_res import get_skin


class CacheStore:
    def __init__(self):
        skin = await get_skin()
        DB.cache_skin(skin)
        tire = await get_tire()
        DB.cache_tire(tire)
        logger.info("皮肤缓存完成")
