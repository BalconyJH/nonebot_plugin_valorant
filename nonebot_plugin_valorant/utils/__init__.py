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


async def generate_database_key(key_path: str=plugin_config.valorant_database_key_path):
    if key_path is None:
        key = Fernet.generate_key()
        try:
            with open("nonebot_plugin_valorant/resources/cache/key.json", "w") as f:
                f.write(f'key: "{key.decode()}"')
        except FileNotFoundError:
            logger.warning("密钥生成失败")
        else:
            logger.info("数据库密钥获取成功")
    else:
        try:
            with open(key_path, "r") as f:
                key = f.read()
        except FileNotFoundError:
            logger.warning("密钥获取失败")
        else:
            logger.info("数据库密钥获取成功")



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
