import os
import asyncio
from uuid import UUID
from pathlib import Path
from contextlib import suppress

import aiohttp
from nonebot import require
from nonebot.log import logger
from cryptography.fernet import Fernet
from nonebot import on_command as _on_command
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

from nonebot_plugin_valorant.config import plugin_config

from ..database import DB
from ..database.db import engine
from .translator import Translator
from .reqlib.client import get_version
from .errors import DatabaseError, AuthenticationError
from .cache import init_cache, cache_store, cache_version

# def on_command(cmd, *args, **kwargs):
#     return _on_command(plugin_config.valorant_command + cmd, *args, **kwargs)

# 全局实例化翻译组件
message_translator = Translator().get_local_translation


async def check_proxy():
    """检查代理是否有效"""
    if plugin_config.valorant_proxies:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://icanhazip.com/",
                    proxy=plugin_config.valorant_proxies,
                    timeout=5,
                ):
                    pass
            except Exception as e:
                raise RuntimeError("代理无效，请检查代理") from e
    logger.info("代理连接成功")


async def check_db():
    if not isinstance(plugin_config.valorant_database, str):
        raise DatabaseError("数据库无效，请检查数据库")

    try:
        with engine.connect():
            data = await DB.get_version()

            if not hasattr(data, "initial"):
                logger.info("数据对象没有 'initial' 属性")
            elif data.initial != "1":
                if await verify_resource_timeliness() is True:
                    logger.info("资源过期，已更新")
                else:
                    logger.info("跳过缓存")
            else:
                await init_cache()

    except (ConnectionError, ProgrammingError):
        await DB.init()
        await init_cache()
    # except Exception as e:
    #     logger.error(f"检查数据库时发生错误：{str(e)}")
    finally:
        engine.dispose()  # 关闭数据库连接


async def generate_database_key():
    """
    生成或获取Valorant插件数据库的密钥。

    参数：
        key_path (str): 可选参数，指定密钥文件的路径，默认为 plugin_config.valorant_database_key_path。

    如果未提供密钥文件路径，则会自动生成一个新的密钥并保存到默认路径下的文件中。
    如果提供了密钥文件路径，则尝试从文件中读取密钥。

    """
    key_path = Path(__file__).parent.parent / "data" / "key.json"

    # 检查密钥文件是否已存在
    if os.path.isfile(key_path):
        # 使用已存在的密钥文件
        try:
            with open(key_path, "r") as f:
                key_str = f.read().encode()
                key = Fernet(key_str)
        except Exception as e:
            logger.warning(f"读取密钥文件时出错：{str(e)}")
        else:
            logger.info(f"秘钥{key_str}读取成功")

    else:
        # 自动生成一个新的密钥并保存到指定路径
        key = Fernet.generate_key()
        key_str = key.decode()
        try:
            with open(key_path, "w") as f:
                f.write(key_str)
        except Exception as e:
            logger.warning(f"生成并保存密钥失败：{str(e)}")
        else:
            logger.info(f"新密钥生成并保存到文件 '{key_path}'")


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


async def verify_resource_timeliness():
    _cache = await DB.get_version()
    _data = await get_version()
    if _cache.manifestId != _data["manifestId"]:
        await cache_version()
        return True


# async def cache_image_resources():


async def on_startup():
    """启动前检查"""
    await asyncio.gather(check_proxy(), check_db(), generate_database_key())


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa


async def user_login_status(
    qq_uid: str,
):
    data = await DB.get_user(qq_uid)
    return data is not None
