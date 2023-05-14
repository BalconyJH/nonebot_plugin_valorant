from datetime import datetime, timezone
from typing import Dict

from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.database.models import BaseModel, User
from nonebot_plugin_valorant.utils.reqlib.auth import Auth

engine = create_engine(plugin_config.valorant_database)
Session = sessionmaker(bind=engine)
session = Session()


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

    @classmethod
    async def get_user(cls, qq_uid: str) -> Dict:
        """
        获取用户信息。

        参数:
        - qq_uid: 用户的 QQ UID。

        返回值:
        - user: 用户信息(Dict)。
        """
        data = User.get(session, qq_uid=qq_uid)
        if datetime.now(timezone.utc) > data["expiry_token"]:
            access_token, entitlements_token = await Auth().refresh_token(data["cookie"])
            data["access_token"] = access_token
            data["entitlements_token"] = entitlements_token
        return data


get_driver().on_startup(DB.init)
get_driver().on_shutdown(DB.close)
