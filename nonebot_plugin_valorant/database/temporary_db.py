from typing import Dict, Any, List

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import String, create_engine, Column, func, DateTime

engine = create_engine("mysql+pymysql://root:070499@localhost:3306/valorant_bot")
session = Session(bind=engine)


class Base(DeclarativeBase):
    pass


# 定义User模型
class User(Base):
    __tablename__ = "user"

    puuid: Mapped[str] = mapped_column(String(255))
    cookie: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(String(255))
    token_id: Mapped[str] = mapped_column(String(255))
    emt: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255))
    expiry_token: Mapped[str] = mapped_column(String(255))
    qq_uid: Mapped[int] = mapped_column(primary_key=True)
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    # group_id: Mapped[str] = mapped_column(String(255))

    def __init__(self, **kw: Any):
        super().__init__()
        self._puuid = None

    @property
    def puuid(self):
        return self._puuid

    @puuid.setter
    def puuid(self, value):
        if not value:
            raise ValueError("puuid 是必需的")
        self._puuid = value


def add_user(user_info: Dict[str, Any]):
    try:
        user = User()
        for key, value in user_info.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e


# 删除用户
def delete_user(puuid: str):
    user = session.query(User).filter_by(puuid=puuid).first()
    session.delete(user)
    session.commit()


# 更新用户
def update_user(puuid: str, update_dict: Dict[str, Any]):
    if user := session.query(User).filter_by(puuid=puuid).first():
        for key, value in update_dict.items():
            setattr(user, key, value)
        session.commit()
    else:
        print(f"User with puuid {puuid} does not exist.")


# 查询用户
def get_user(puuid: str) -> Dict[str, Any]:
    user = session.query(User).filter_by(puuid=puuid).first()
    return user.__dict__


# 查询所有用户
def get_all_users() -> List[Dict[str, Any]]:
    users = session.query(User).all()
    return [user.__dict__ for user in users]


def init():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"表创建失败: {e}")


# if __name__ == '__main__':
#     init()
