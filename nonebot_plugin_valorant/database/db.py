from sqlalchemy import String, create_engine, Column, func, DateTime
from sqlalchemy_utils import database_exists, create_database
from nonebot_plugin_valorant.database.models import Base
from contextlib import suppress
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine("mysql+pymysql://root:070499@localhost:3306/valorant_bot")


class DB:
    @classmethod
    async def init(cls):
        with suppress(ValueError):
            create_database(engine.url)
        with suppress(SQLAlchemyError):
            Base.metadata.create_all(engine)

    @classmethod
    async def create_database(cls):
        if not database_exists(engine.url):
            create_database(engine.url)
        return True


async def main():
    await DB.init()
    print("数据库初始化完成")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
