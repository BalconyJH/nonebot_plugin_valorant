# 导入所需的模块和函数
import random
import string
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from temporary_db import add_user, init

# 创建连接引擎和会话对象
engine = create_engine("mysql+pymysql://root:070499@localhost:3306/valorant_bot")
session = Session(bind=engine)


# 生成随机数据
random_str = lambda n: ''.join(random.choices(string.ascii_letters + string.digits, k=n))
user_info: Dict[str, Any] = {
    "puuid": random_str(10),
    "cookie": random_str(20),
    "access_token": random_str(30),
    "token_id": random_str(40),
    "emt": random_str(50),
    "username": random_str(10),
    "region": random_str(5),
    "expiry_token": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "qq_uid": random.randint(100000, 999999),
}

# 插入数据
add_user(user_info)

# 关闭会话
session.close()
