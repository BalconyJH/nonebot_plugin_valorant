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


async def generate_database_key(key_path: str = plugin_config.valorant_database_key_path):
    """
    生成或获取Valorant插件数据库的密钥。

    参数：
        key_path (str): 可选参数，指定密钥文件的路径，默认为plugin_config.valorant_database_key_path。

    如果未提供密钥文件路径，则会自动生成一个新的密钥并保存到默认路径下的文件中。
    如果提供了密钥文件路径，则尝试从文件中读取密钥。

    """

    if key_path is None:
        # 自动生成一个新的密钥
        key = Fernet.generate_key()
        default_key_path = "nonebot_plugin_valorant/data/key.json"
        try:
            with open(default_key_path, "w") as f:
                f.write(key.decode())
        except FileNotFoundError:
            logger.warning("密钥生成失败")
        else:
            logger.info("数据库密钥获取成功")
    else:
        # 从指定路径读取密钥
        try:
            with open(key_path, "r") as f:
                f.read()
        except FileNotFoundError:
            logger.warning("密钥获取失败")
        else:
            logger.info("数据库密钥获取成功")



async def on_startup():
    """启动前检查"""
    await asyncio.gather(
        check_proxy(), check_db(), init_cache(), generate_database_key()
    )


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa
