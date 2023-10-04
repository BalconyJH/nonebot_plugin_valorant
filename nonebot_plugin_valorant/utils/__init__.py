import os
import asyncio
from uuid import UUID
from pathlib import Path
from contextlib import suppress
from urllib.parse import urlparse

import aiohttp
from nonebot import require
from nonebot.log import logger
from cryptography.fernet import Fernet
from nonebot import on_command as _on_command
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from aiohttp.client_exceptions import InvalidURL, ClientConnectorError

from nonebot_plugin_valorant.config import plugin_config

from ..database import DB
from ..database.db import engine
from .translator import Translator
from .requestlib.client import get_version
from .cache import init_cache, cache_store, cache_version
from .errors import (
    DatabaseError,
    ResponseError,
    ConfigurationError,
    AuthenticationError,
)

# def on_command(cmd, *args, **kwargs):
#     return _on_command(plugin_config.valorant_command + cmd, *args, **kwargs)

# 全局实例化翻译组件
message_translator = Translator().get_local_translation


async def check_proxy():
    """检查代理是否有效"""
    if plugin_config.valorant_proxies is not None:
        await _verify_url_legality(plugin_config.valorant_proxies)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://icanhazip.com/",
                    proxy=plugin_config.valorant_proxies,
                    timeout=5,
                ):
                    logger.info("代理连接测试成功")
            except ClientConnectorError as e:
                logger.warning(f"代理连接错误: {e}")


async def _check_database_validity() -> None:
    """检查数据库是否有效。

    本函数将检查数据库是否有效，如果无效则会抛出 DatabaseError 异常。

    返回:
        无返回值。

    异常:
        如果数据库无效，则会抛出 DatabaseError 异常。

    用法:
        ```python
        await _check_database_validity()
        ```
    """
    if not isinstance(plugin_config.valorant_database, str):
        raise DatabaseError("数据库无效，请检查数据库")


async def _verify_db_resource(_cache) -> None:
    """异步初始化数据库或验证资源时效性。

    本函数根据传入的 _cache 对象的 'initial' 属性来执行相应操作。

    返回:
        无返回值。

    异常:
        本函数可能会抛出与数据库连接和初始化相关的异常。

    用法:
        ```python
        await initialize_or_verify_db_resource(_cache)
        ```
    """
    if not hasattr(_cache, "initial") or _cache.initial is False:
        await DB.init()
        await init_cache()
        logger.info("数据库初始化完成")

    if _cache.initial is True:
        if await _verify_resource_timeliness(_cache):
            logger.info(f"资源值{_cache.manifestId}已是最新")
        else:
            logger.info("资源过期，已更新")


async def check_db():
    try:
        await _check_database_validity()

        with engine.connect():
            _cache = await DB.get_version()
            await _verify_db_resource(_cache)

    except (ConnectionError, ProgrammingError):
        logger.warning("数据库检查失败，尝试初始化数据库")
        await DB.init()
        await init_cache()
        logger.info("数据库初始化完成")
    finally:
        engine.dispose()


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
            logger.info("秘钥读取成功")

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


async def verify_uuid_legality(uuid: str):
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
        return False


async def _verify_url_legality(url: str):
    if not url:
        logger.warning("URL为空")
    result = urlparse(url)
    if not all([result.scheme, result.netloc]):
        raise ConfigurationError("URL格式错误，请检查URL格式")


async def _verify_resource_timeliness(_cache) -> bool:
    try:
        _data = await get_version()
        if _cache.manifestId == _data["manifestId"]:
            return True
        await init_cache()
        return False
    except (ResponseError, SQLAlchemyError) as e:
        if e is ResponseError:
            logger.error(f"获取版本信息失败：{str(e)}")
        elif e is SQLAlchemyError:
            raise DatabaseError(f"数据库错误：{str(e)}") from e


# async def cache_image_resources():


async def on_startup():
    """启动前检查"""
    # await _verify_url_legality(plugin_config.valorant_proxies)
    await check_proxy()
    await check_db()
    await generate_database_key()


require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa


async def user_login_status(
    qq_uid: str,
):
    data = await DB.get_user(qq_uid)
    return data is not None
