import asyncio

from nonebot import get_driver
from nonebot.log import logger
from nonebot.plugin.manager import PluginLoader

from nonebot_plugin_valorant.config import Config
from nonebot_plugin_valorant.utils import on_startup

driver = get_driver()


@driver.on_startup
async def init(**kwargs):
    try:
        await on_startup()
    except RuntimeWarning as error:
        logger.debug(f"loop不存在{error},尝试新建loop开始初始化")
        asyncio.run(await on_startup())

    from . import plugins  # noqa: F401
