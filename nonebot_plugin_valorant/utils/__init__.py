import asyncio

import aiohttp
from cryptography.fernet import Fernet
from nonebot import on_command as _on_command, require
from nonebot.log import logger

from nonebot_plugin_valorant.config import plugin_config
from .cache import cache_store, init_cache
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
            except Exception as e:
                raise RuntimeError("代理无效，请检查代理") from e
    logger.info("代理连接成功")


async def check_db():
    """检查数据库是否有效"""
    try:
        await DB.init()
        engine.connect()
    except Exception as e:
        raise DatabaseError(f"数据库无效，请检查数据库{e}") from e
    engine.dispose()  # 关闭数据库连接
    logger.info("数据库连接成功")


async def generate_database_key():
    key = Fernet.generate_key()
    # 在nonebot_plugin_valorant/resources/cache创建一个conf.yaml文件保存key
    with open("nonebot_plugin_valorant/resources/cache/conf.yaml", "w") as f:
        f.write(f'key: "{key.decode()}"')
    logger.info("数据库密钥生成成功")


async def on_startup():
    """启动前检查"""
    await asyncio.gather(
        check_proxy(),
        check_db(),
        init_cache(),
        generate_database_key()
    )


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa
