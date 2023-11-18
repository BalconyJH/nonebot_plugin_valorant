from nonebot import get_driver
from nonebot.log import logger
from sqlalchemy import create_engine
from cryptography.fernet import Fernet
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.utils.errors import DatabaseError
from nonebot_plugin_valorant.database.models import Tier, User, Version, BaseModel, SkinsStore, WeaponSkins  # UserShop,

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
        try:
            await cls._create_database()
            await cls._create_tables()
        except SQLAlchemyError as e:
            raise DatabaseError(f"数据库初始化失败{e}") from e

    @staticmethod
    async def _create_database():
        """
        创建数据库（如果不存在）。
        """
        try:
            if not database_exists(engine.url):
                create_database(engine.url)
                logger.debug("创建数据库成功")
        except SQLAlchemyError as e:
            logger.error(f"创建数据库失败{e}")

    @staticmethod
    async def _create_tables():
        """
        创建表格。
        """
        try:
            BaseModel.metadata.create_all(engine)
            logger.info("创建表成功")
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
    async def get_user(cls, qq_uid: str):
        """
        获取用户信息。

        参数:
        - qq_uid: 用户的 QQ UID。

        返回值:
        - user: 用户信息(Dict)。
        """
        return (await User.get(session, qq_uid=qq_uid)).first()

    @classmethod
    async def update_user(cls, filter_by: dict, update_values: dict):
        """
        更新用户信息。

        参数:
        - session: SQLAlchemy 的 Session 对象。
        - filter_by: 用于筛选记录的字段和值。
        - update_values: 用于更新记录的字段和新值。
        """
        await User.update(session, filter_by=filter_by, update_values=update_values)

    @classmethod
    async def cache_skin(cls, data: dict):
        """
        缓存商店信息。

        参数:
        """
        for uuid, skin_data in data.items():
            existing_skin = await WeaponSkins.get(session, uuid=uuid)
            if existing_skin.first() is not None:
                continue
            await WeaponSkins.add(session, **skin_data)
        logger.info("skin缓存完成")

    @classmethod
    async def cache_tier(cls, data: dict):
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
    async def get_version(cls):
        """
        查询版本信息。

        返回值:
        - version: 版本信息。
        """
        return (await Version.get(session)).first()

    @classmethod
    async def update_version(cls, **kwargs):
        """
        更新版本信息。

        参数:
        - kwargs: 包含版本信息的关键字参数。
        """
        try:
            version_cache = await DB.get_version()
        except KeyError as e:
            raise DatabaseError("版本信息不存在") from e

        if version_cache is None:
            await Version.add(session, **kwargs)
        elif version_cache.manifestId == kwargs["manifestId"]:
            logger.info("版本信息已是最新")

        else:
            await Version.add(session, **kwargs)
            await Version.delete(session, manifestId=version_cache.manifestId)
            logger.info("版本信息已刷新")

    @classmethod
    async def init_version(cls, filter_by: dict, update_value: dict):
        await Version.update(session, filter_by, update_value)

    # @classmethod
    # async def update_user_store_offer(cls, **kwargs: object):
    #     """
    #     更新用户商店信息。
    #
    #     参数:
    #     - kwargs: 包含用户商店信息的关键字参数。
    #     """
    #     UserShop.update(session, **kwargs)

    # @classmethod
    # async def refresh_token(cls, **kwargs: object):
    #     """
    #     更新用户商店信息。
    #
    #     参数:
    #     - kwargs: 包含用户商店信息的关键字参数。
    #     """
    #     await User.update(session, **kwargs)

    @classmethod
    async def get_skin(cls, uuid: str):
        """
        获取武器皮肤信息。

        参数:
        - uuid: 武器皮肤的 UUID。

        返回值:
        - skins: 武器皮肤信息。
        """
        return (await WeaponSkins.get(session, uuid=uuid)).first()

    @classmethod
    async def get_all_skins_icon(cls):
        """
        获取所有武器皮肤的图标。

        返回值:
        - skins: 武器皮肤图标。
        """
        return (await WeaponSkins.get(session, WeaponSkins.uuid, WeaponSkins.icon)).all()

    @classmethod
    async def cache_player_skins_store(cls, **kwargs):
        """
        缓存用户商店信息。

        参数:
        - kwargs: 包含用户商店信息的关键字参数。
        """
        await SkinsStore.add(session, **kwargs)

    @classmethod
    async def delete_player_skins_store(cls, qq_uid: str):
        """
        删除用户商店信息。

        参数:
        - qq_uid: 用户的 QQ UID。
        """
        await SkinsStore.delete(session, qq_uid=qq_uid)

    @classmethod
    async def get_player_skins_store(cls, qq_uid: str):
        """
        获取用户商店信息。

        参数:
        - qq_uid: 用户的 QQ UID。

        返回值:
        - skins: 用户商店信息。
        """
        return (await SkinsStore.get(session, qq_uid=qq_uid)).first()


get_driver().on_shutdown(DB.close)
