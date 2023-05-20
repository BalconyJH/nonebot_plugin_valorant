import asyncio

from nonebot import get_driver
from nonebot.plugin.manager import PluginLoader

from nonebot_plugin_valorant.config import Config
from nonebot_plugin_valorant.utils import on_startup

if isinstance(globals()["__loader__"], PluginLoader):
    global_config = get_driver().config
    config = Config.parse_obj(global_config)
    # from .utils import on_startup

asyncio.run(on_startup())
from . import plugins  # noqa: F401
