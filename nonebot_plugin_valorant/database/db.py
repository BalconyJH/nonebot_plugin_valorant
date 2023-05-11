from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.database.models import BaseModel, User

engine = create_engine(plugin_config.valorant_database)
Session = sessionmaker(bind=engine)
session = Session()


class DB:
    @classmethod
    async def init(cls):
        await cls._create_database()
        await cls._create_tables()
        logger.info("数据库初始化完成")

    @staticmethod
    async def _create_database():
        try:
            if not database_exists(engine.url):
                create_database(engine.url)
        except SQLAlchemyError as e:
            logger.error(f"创建数据库失败{e}")

    @staticmethod
    async def _create_tables():
        try:
            BaseModel.metadata.create_all(engine)
        except SQLAlchemyError as e:
            logger.error(f"创建表失败{e}")

    @staticmethod
    async def close():
        engine.dispose()

    @classmethod
    async def login(cls, **kwargs):
        User.add(session, **kwargs)
        return True

    @classmethod
    async def logout(cls, qq_uid: str):
        User.delete(session, qq_uid=qq_uid)
        return True


get_driver().on_startup(DB.init)
get_driver().on_shutdown(DB.close)
