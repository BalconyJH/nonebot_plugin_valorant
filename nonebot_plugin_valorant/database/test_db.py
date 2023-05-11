import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_insert_user():
    # 创建数据库引擎
    engine = create_engine('mysql+pymysql://root:070499@localhost:3306/valorant_bot')

    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()

    # 导入 User 模型
    from nonebot_plugin_valorant.database.models import User


    # 创建示例用户
    user = User(
        puuid='example_puuid',
        cookie=json.dumps(cookie),
        access_token='example_access_token',
        token_id='example_token_id',
        emt='example_emt',
        username='example_username',
        region='example_region',
        expiry_token='example_expiry_token',
        qq_uid='example_qq_uid'
    )

    # 将示例用户插入数据库
    session.add(user)
    session.commit()

    # 打印插入的用户信息
    print(user)

    # 关闭会话
    session.close()


# 调用测试函数
test_insert_user()
