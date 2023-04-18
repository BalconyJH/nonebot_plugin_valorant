from tortoise.fields.data import BooleanField, CharField, IntField, TextField, FloatField
from tortoise.models import Model


class BaseModel(Model):
    @classmethod
    def get_(cls, *args, **kwargs):
        super().get(*args, **kwargs)

    @classmethod
    def get(cls, **kwargs):
        return cls.filter(**kwargs)

    @classmethod
    async def add(cls, **kwargs):
        puuid = kwargs.get("puuid")
        if not puuid:
            raise ValueError("puuid is required")

        if await cls.filter(puuid=puuid).exists():
            return False

        await cls.create(**kwargs)
        return True

    @classmethod
    async def delete(cls, **kwargs):
        query = cls.get(**kwargs)
        if await query.exists():
            await query.delete()
            return True
        return False

    @classmethod
    async def update(cls, q, **kwargs):
        query = cls.get(**q)
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
