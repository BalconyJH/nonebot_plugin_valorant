from typing import Any, Dict

from cryptography.fernet import Fernet
from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy_utils import database_exists, create_database

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.database.models import (
    BaseModel,
    Tier,
    User,
    Version,
    WeaponSkin,
    UserShop,
)

engine = create_engine(plugin_config.valorant_database)
Session = sessionmaker(bind=engine)
session = Session()

# 生成密钥
database_key = Fernet.generate_key()

cipher_suite = Fernet(database_key)


def encrypt_data(data: str) -> bytes:
    return cipher_suite.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes) -> str:
    return cipher_suite.decrypt(encrypted_data).decode()


def calculate_hash(data: str) -> int:
    return hash(data)


class DB:
    @classmethod
    async def init(cls):
        """
        初始化数据库。创建数据库和表格。
        """
        await cls._create_database()
        await cls._create_tables()
        logger.info("数据库初始化完成")

    @staticmethod
    async def _create_database():
        """
        创建数据库（如果不存在）。
        """
        try:
            if not database_exists(engine.url):
                create_database(engine.url)
        except SQLAlchemyError as e:
            logger.error(f"创建数据库失败{e}")

    @staticmethod
    async def _create_tables():
        """
        创建表格。
        """
        try:
            BaseModel.metadata.create_all(engine)
        except SQLAlchemyError as e:
            logger.error(f"创建表失败{e}")

    @staticmethod
    async def close():
        """
        关闭数据库连接。
        """
        engine.dispose()

    @classmethod
    async def login(cls, **kwargs):
        """
        用户登录。将用户添加到数据库中。

        参数:
        - kwargs: 包含用户信息的关键字参数。
        """
        await User.add(session, **kwargs)

    @classmethod
    async def logout(cls, qq_uid: str):
        """
        用户登出。从数据库中删除指定的用户。

        参数:
        - qq_uid: 用户的 QQ UID。
        """
        await User.delete(session, qq_uid=qq_uid)
        # todo 级联删除用户的所有数据(shop, user, misson, etc.)

    @classmethod
    async def get_user(cls, qq_uid: str) -> Query:
        """
        获取用户信息。

        参数:
        - qq_uid: 用户的 QQ UID。

        返回值:
        - user: 用户信息(Dict)。
        """
        user = await User.get(session, qq_uid=qq_uid)
        return user.first()

    @classmethod
    async def cache_skin(cls, data: Dict):
        """
        缓存商店信息。

        参数:
        """
        for uuid, skin_data in data.items():
            existing_skin = await WeaponSkin.get(session, uuid=uuid)
            if existing_skin.first() is not None:
                continue
            await WeaponSkin.add(session, **skin_data)
        logger.info("skin缓存完成")

    @classmethod
    async def cache_tier(cls, data: Dict):
        """
        缓存段位信息。

        参数:
        """
        for uuid, tier_data in data.items():
            existing_tier = await Tier.get(session, uuid=uuid)
            if existing_tier.first() is not None:
                continue
            await Tier.add(session, **tier_data)
        logger.info("tier缓存完成")

    # @classmethod
    # async def cache_version(cls, data: Dict):
    #     """
    #     缓存版本信息。
    #
    #     参数:
    #     - data: 版本数据字典，包含多个版本的信息
    #     """
    #     for version_data in data:

    @classmethod
    async def get_version(cls, version_fields) -> dict[Any, Any]:
        """
        查询版本信息。

        参数:
        - session: 数据库会话对象
        - version_fields: 版本字段列表，包含要查询的版本字段名

        返回:
        - 查询结果的字典，键为版本字段名，值为对应的内容
        """
        return await Version.get(session, **version_fields)

    @classmethod
    async def update_version(cls, **kwargs):
        """
        更新版本信息。

        参数:
        - kwargs: 包含版本信息的关键字参数。
        """
        manifest_id = kwargs["manifestId"]
        version_cache = await Version.get(session, manifestId=manifest_id)

        if version_cache.first() is None:
            await Version.add(session, **kwargs)
        else:
            existing_version = version_cache.first()
            if existing_version.manifestId != manifest_id:
                await Version.update(session, manifestId=manifest_id, **kwargs)
            logger.info("版本信息已存在")


    @classmethod
    async def init_version(cls, **kwargs):
        await Version.add(session, **kwargs)


    @classmethod
    async def update_user_store_offer(cls, **kwargs: object):
        """
        更新用户商店信息。

        参数:
        - kwargs: 包含用户商店信息的关键字参数。
        """
        await UserShop.update(session, **kwargs)

# nonebot启动时初始化/关闭数据库
# get_driver().on_startup(DB.init)
get_driver().on_shutdown(DB.close)
