from tortoise.fields.data import BooleanField, CharField, IntField, TextField, FloatField

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from nonebot_plugin_datastore import get_plugin_data, get_session


# class Base(DeclarativeBase):
#     @classmethod
#     def filter(cls, **kwargs):
#         """返回符合给定条件的模型实例的 QuerySet 对象"""
#         return cls.filter(**kwargs)
#
#     @classmethod
#     async def create(cls, **kwargs):
#         """创建一个新的模型实例"""
#         if puuid := kwargs.get("puuid"):
#             return (
#                 None
#                 if await cls.filter(puuid=puuid).exists()
#                 else await cls.create(**kwargs)
#             )
#         else:
#             raise ValueError("puuid 是必需的")
#
#     @classmethod
#     async def delete(cls, **kwargs):
#         """删除符合给定条件的模型实例"""
#         query = cls.filter(**kwargs)
#         if await query.exists():
#             await query.delete()
#             return True
#         return False
#
#     @classmethod
#     async def update(cls, q, **kwargs):
#         """更新符合给定条件的模型实例"""
#         query = cls.filter(**q)
#         if await query.exists():
#             await query.update(**kwargs)
#             return True
#         return False
#
#     class Meta:
#         abstract = True

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    puuid: Mapped[str] = mapped_column(primary_key=True, unique=True)
    cookie: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(String(255))
    token_id: Mapped[str] = mapped_column(String(255))
    emt: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255))
    expiry_token: Mapped[str] = mapped_column(String(255))
    qq_uid: Mapped[str] = mapped_column(String(255))
    group_id: Mapped[str] = mapped_column(String(255))


class Skin(Base):
    __tablename__ = "shop"
