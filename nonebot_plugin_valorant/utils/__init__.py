import aiohttp
from nonebot import on_command as _on_command, require
from sqlalchemy.exc import OperationalError

from nonebot_plugin_valorant.config import plugin_config
from .errors import AuthenticationError, DatabaseError
from ..database import DB
from ..database.db import engine


def on_command(cmd, *args, **kwargs):
    return _on_command(plugin_config.valorant_command + cmd, *args, **kwargs)


async def check_proxy():
    """检查代理是否有效"""
    if plugin_config.valorant_proxies:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://icanhazip.com/",
                    proxy=plugin_config.valorant_proxies,
                    timeout=2,
                ):
                    pass
            except aiohttp.ClientError as e:
                raise RuntimeError("代理无效，请检查代理") from e


async def check_db():
    """检查数据库是否有效"""
    try:
        await DB.init()
        await engine.connect()
    except OperationalError as e:
        raise DatabaseError("数据库无效，请检查数据库") from e
    await engine.dispose()  # 关闭数据库连接


def on_startup():
    """启动前检查"""
    check_proxy()
    check_db()


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa
