from tortoise import Tortoise, run_async
from tortoise.fields import TextField, BooleanField, CharField, IntField, DecimalField
from tortoise.models import Model


# from nonebot_plugin_valorant import config


# 定义User模型
class User(Model):
    puuid = CharField(max_length=50, pk=True, unique=True)
    cookie = TextField(null=True)
    access_token = TextField(null=True)
    token_id = CharField(max_length=100, null=True)
    emt = CharField(max_length=100, null=True)
    username = CharField(max_length=50, null=True)
    region = CharField(max_length=10, null=True)
    expiry_token = CharField(max_length=100, null=True)
    qq_uid = CharField(max_length=20, null=True)
    group_id = CharField(max_length=20, null=True)


# 定义Shop模型
class Shop(Model):
    is_price = BooleanField()
    timestamp = CharField(max_length=50, null=True)
    uuid = CharField(max_length=255, pk=True, unique=True)
    name = CharField(max_length=50)
    price = DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_pct = IntField(null=True)


# 连接MySQL数据库
async def connect_to_db():
    await Tortoise.init(
        db_url='mysql://root:070499@localhost:3306/valorant_bot',  # MySQL连接URL
        modules={'models': ['__main__']})

    # 创建表
    await Tortoise.generate_schemas()


# 运行异步程序
if __name__ == '__main__':
    run_async(connect_to_db())
