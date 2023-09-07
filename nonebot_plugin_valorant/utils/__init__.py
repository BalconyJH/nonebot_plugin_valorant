import asyncio
from uuid import UUID

import aiohttp
from nonebot import require
from nonebot.log import logger
from cryptography.fernet import Fernet
from nonebot import on_command as _on_command

from nonebot_plugin_valorant.config import plugin_config

from ..database import DB
from ..database.db import engine
from .cache import init_cache, cache_store
from .errors import DatabaseError, AuthenticationError

# def on_command(cmd, *args, **kwargs):
#     return _on_command(plugin_config.valorant_command + cmd, *args, **kwargs)


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
    if isinstance(plugin_config.valorant_database, str):
        try:
            engine.connect()
            print(await DB.get_version())
            if await DB.initial_value("initial") is None:
                await DB.init()
                # await DB.update_version(initial=True)
                await init_cache()
        except ConnectionError:
            await DB.init()
            # await DB.update_version(initial=True)
            await init_cache()
        engine.dispose()  # 关闭数据库连接
    else:
        raise DatabaseError("数据库无效，请检查数据库")


async def generate_database_key(
    key_path: str = plugin_config.valorant_database_key_path,
):
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


async def verify_uuid_legal(uuid: str):
    """
    Verify if the given UUID is legal.

    Args:
        uuid (str): The UUID to be verified.

    Returns:
        int: The version number of the UUID.

    Raises:
        ValueError: If the UUID is not in a valid format.
    """
    try:
        uuid_obj = UUID(uuid)
        return uuid_obj.version
    except ValueError:
        raise


# async def cache_image_resources():


async def on_startup():
    """启动前检查"""
    await asyncio.gather(check_proxy(), check_db(), generate_database_key())


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa


async def user_login_status(
    qq_uid: str,
):
    if await DB.get_user(qq_uid) is None:
        return False
    else:
        return True
