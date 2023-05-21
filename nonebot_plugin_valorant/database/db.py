from typing import Dict, Any

from cryptography.fernet import Fernet
from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy_utils import database_exists, create_database

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.database.models import (
    BaseModel,
    User,
    WeaponSkin,
    Tier,
    Version,
)

engine = create_engine(plugin_config.valorant_database)
Session = sessionmaker(bind=engine)
session = Session()

# 生成密钥
key = Fernet.generate_key()

cipher_suite = Fernet(key)


# 加密数据
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())


# 解密数据
def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode()


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
        User.add(session, **kwargs)

    @classmethod
    async def logout(cls, qq_uid: str):
        """
        用户登出。从数据库中删除指定的用户。

        参数:
        - qq_uid: 用户的 QQ UID。
        """
        User.delete(session, qq_uid=qq_uid)
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
        return User.get(session, qq_uid=qq_uid)

    @classmethod
    async def cache_skin(cls, data: Dict):
        """
        缓存商店信息。

        参数:
        """
        for uuid, skin_data in data.items():
            existing_skin = WeaponSkin.get(session, uuid=uuid).first()  # 查询现有数据
            if existing_skin and existing_skin.matches_data(skin_data):  # 检查数据是否相同
                continue  # 数据已存在且相同，跳过添加逻辑
            WeaponSkin.merge(session, **skin_data)

    @classmethod
    async def cache_tier(cls, data: Dict):
        """
        缓存段位信息。

        参数:
        """
        for uuid, tier_data in data.items():
            existing_tier = Tier.get(session, uuid=uuid).first()  # 查询现有数据
            if existing_tier and existing_tier.matches_data(tier_data):  # 检查数据是否相同
                continue  # 数据已存在且相同，跳过添加逻辑
            Tier.merge(session, **tier_data)

    # @classmethod
    # async def cache_version(cls, data: Dict):
    #     """
    #     缓存版本信息。
    #
    #     参数:
    #     - data: 版本数据字典，包含多个版本的信息
    #     """
    #     for version_data in data:
    #

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
        return Version.get(session, **version_fields)

    @classmethod
    async def update_version(cls, **kwargs):
        """
        更新版本信息。

        参数:
        - kwargs: 包含版本信息的关键字参数。
        """
        Version.update(session, **kwargs)

    @classmethod
    async def init_version(cls, **kwargs):
        Version.add(session, **kwargs)


# nonebot启动时初始化/关闭数据库
# get_driver().on_startup(DB.init)
get_driver().on_shutdown(DB.close)
