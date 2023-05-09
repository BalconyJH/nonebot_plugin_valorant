from sqlalchemy import String, create_engine, Column, func, DateTime
from sqlalchemy_utils import database_exists, create_database
from nonebot_plugin_valorant.database.models import BaseModel
from contextlib import suppress
from nonebot.log import logger
from nonebot_plugin_valorant.config import plugin_config
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine(plugin_config.valorant_database)


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
