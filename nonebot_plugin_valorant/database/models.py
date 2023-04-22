from tortoise.fields.data import BooleanField, CharField, IntField, TextField, FloatField

from tortoise.models import Model


class BaseModel(Model):
    @classmethod
    def filter(cls, **kwargs):
        """返回符合给定条件的模型实例的 QuerySet 对象"""
        return cls.filter(**kwargs)

    @classmethod
    async def create(cls, **kwargs):
        """创建一个新的模型实例"""
        if puuid := kwargs.get("puuid"):
            return (
                None
                if await cls.filter(puuid=puuid).exists()
                else await cls.create(**kwargs)
            )
        else:
            raise ValueError("puuid 是必需的")

    @classmethod
    async def delete(cls, **kwargs):
        """删除符合给定条件的模型实例"""
        query = cls.filter(**kwargs)
        if await query.exists():
            await query.delete()
            return True
        return False

    @classmethod
    async def update(cls, q, **kwargs):
        """更新符合给定条件的模型实例"""
        query = cls.filter(**q)
        if await query.exists():
            await query.update(**kwargs)
            return True
        return False

    class Meta:
        abstract = True


class User(BaseModel):
    puuid = TextField(pk=True, unique=True)
    cookie = TextField()
    access_token = TextField()
    token_id = TextField()
    emt = TextField()
    username = TextField()
    region = TextField()
    expiry_token = TextField()
    qq_uid = CharField(max_length=20)
    group_id = CharField(max_length=20)


class Shop(BaseModel):
    is_price = BooleanField()
    timestamp = TextField()
    id = CharField(max_length=255)
    name = CharField(max_length=20)
    price = FloatField()
    discount = FloatField()
    discount_pct = IntField()
