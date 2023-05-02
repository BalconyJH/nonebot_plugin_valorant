from typing import Dict, Any, List, TypedDict, Optional

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import String, create_engine, Column, func, DateTime

engine = create_engine("mysql+pymysql://root:070499@localhost:3306/valorant_bot")
session = Session(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    """用户模型类

    该模型表示一个用户，包含了用户的各种信息，例如唯一标识符、cookie、access token等。
    """

    __tablename__ = "user"

    puuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    """str: 用户的唯一标识符，作为主键。"""

    cookie: Mapped[str] = mapped_column(String(255))
    """str: 用户的cookie。"""

    access_token: Mapped[str] = mapped_column(String(255))
    """str: 用户的access token。"""

    token_id: Mapped[str] = mapped_column(String(255))
    """str: 用户的token id。"""

    emt: Mapped[str] = mapped_column(String(255))
    """str: 用户的emt。"""

    username: Mapped[str] = mapped_column(String(255))
    """str: 用户的用户名。"""

    region: Mapped[str] = mapped_column(String(255))
    """str: 用户所在的地区。"""

    expiry_token: Mapped[str] = mapped_column(String(255))
    """str: access token的过期时间。"""

    qq_uid: Mapped[int] = mapped_column(String(30), nullable=False)
    """int: 用户的QQ uid。"""

    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())
    """DateTime: 用户信息的更新时间。"""

    # group_id: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<User(puuid='{self.puuid}', cookie='{self.cookie}', access_token='{self.access_token}', token_id='{self.token_id}', emt='{self.emt}', username='{self.username}', region='{self.region}', expiry_token='{self.expiry_token}', qq_uid='{self.qq_uid}', timestamp='{self.timestamp}')>"


class WeaponSkin(Base):
    """武器皮肤模型类

    该模型表示一种武器皮肤，包含唯一标识符、名称、图标和级别四个属性。
    """

    __tablename__ = "weapon_skins"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    """str: 武器皮肤的唯一标识符，作为主键。"""

    names: Mapped[str] = mapped_column(String(255))
    """str: 武器皮肤的名称。"""

    icon: Mapped[str] = mapped_column(String(255))
    """str: 武器皮肤的图标。"""

    tier: Mapped[str] = mapped_column(String(255))
    """str: 武器皮肤的级别。"""

    def __repr__(self):
        return f"<WeaponSkin(uuid='{self.uuid}', names='{self.names}', icon='{self.icon}', tier='{self.tier}')>"


class Version(Base):
    __tablename__ = "version"

    valorant_client_version: Mapped[str] = mapped_column(String(255))

    bot_version: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Version(valorant_client_version='{self.valorant_client_version}', bot_version='{self.bot_version}')>"


class Tier(Base):
    __tablename__ = "tier"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[int] = mapped_column(String(255))

    icon: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Tier(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"


class Mission(Base):
    __tablename__ = "mission"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    titles: Mapped[str] = mapped_column(String(255))

    type: Mapped[str] = mapped_column(String(255))

    progress: Mapped[str] = mapped_column(String(255))

    xp: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Mission(uuid='{self.uuid}', titles='{self.titles}', type='{self.type}', progress='{self.progress}', xp='{self.xp}')>"


class Playercard(Base):
    __tablename__ = "playercard"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    icon: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return (
            f"<Playercard(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"
        )


class Title(Base):
    __tablename__ = "title"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    text: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Title(uuid='{self.uuid}', name='{self.name}', icon='{self.text}')>"


class UserStore(Base):
    qq_uid: Mapped[int] = mapped_column(String(30), nullable=False)
    puuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    #  TODO: add more fields


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
def delete_user(qq_uid: int, username: Optional[str] = None):  # TODO: 删除关联表
    if username is not None:
        user = session.query(User).filter_by(username=username, qq_uid=qq_uid).first()
        if user is None:
            raise ValueError(
                f"No user found with username '{username}' and qq_uid '{qq_uid}'"
            )
        session.delete(user)
    else:
        users = session.query(User).filter_by(qq_uid=qq_uid).all()
        if len(users) == 0:
            raise ValueError(f"No user found with qq_uid '{qq_uid}'")
        for user in users:
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


if __name__ == "__main__":
    init()
