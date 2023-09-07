import asyncio

from nonebot import get_driver
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from nonebot_plugin_valorant.config import Config
from nonebot_plugin_valorant.utils import on_startup

from .config import plugin_config

driver = get_driver()

__plugin_name_meta__ = PluginMetadata(
    name="nonebot_plugin_valorant",
    description="Valorant查询插件",
    usage="",
    type="application",
    homepage="https://github.com/BalconyJH/nonebot_plugin_valorant",
    config=plugin_config,
)


@driver.on_startup
async def init(**kwargs):
    try:
        await on_startup()
    except RuntimeWarning as error:
        logger.debug(f"loop不存在{error},尝试新建loop开始初始化")
        asyncio.run(await on_startup())

    from . import plugins  # noqa: F401
