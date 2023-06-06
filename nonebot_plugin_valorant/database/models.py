from typing import Dict

from sqlalchemy import String, Column, func, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def get(cls, session, **kwargs):
        query = session.query(cls).filter_by(**kwargs)
        return query.first()

    @classmethod
    def add(cls, session, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()

    @classmethod
    def delete(cls, session, **kwargs):
        query = cls.get(session, **kwargs)
        if query.count():
            query.delete()
            session.commit()
            return True
        return False

    @classmethod
    def update(cls, session, q):
        query = cls.get(session, **q)
        if query.count():
            query.update(q)
            session.commit()
            return True
        return False

    @classmethod
    def matches_data(cls, data: Dict) -> bool:
        """
        检查数据UUID是否与模型匹配。
        :param
        - data:["uuid"]
        :return:
        - bool: 数据UUID与模型匹配返回True，否则返回False。
        """
        # return data.get("uuid") == str(cls.uuid)
        # TODO: 检查数据是否匹配, 添加读取数据库uuid比对

    @classmethod
    def merge(cls, session, **kwargs):
        query = cls.get(session, uuid=kwargs["uuid"])
        if query.count():
            query.update(kwargs)
            session.commit()
        else:
            cls.add(session, **kwargs)


class User(BaseModel):
    """用户模型类

    该模型表示一个用户，包含了用户的各种信息，例如唯一标识符、cookie、access token等。
    """

    __tablename__ = "user"

    puuid: Mapped[str] = mapped_column(String(255))
    """str: 用户的唯一标识符"""

    cookie: Mapped[JSON] = mapped_column(JSON)
    """JSON: 用户的cookie。"""

    access_token: Mapped[Text] = mapped_column(Text)
    """Text: 用户的access token。"""

    token_id: Mapped[Text] = mapped_column(Text)
    """Text: 用户的token id。"""

    emt: Mapped[Text] = mapped_column(Text)
    """Text: 用户的entitlements_token。"""

    username: Mapped[str] = mapped_column(String(255))
    """str: 用户的用户名。"""

    region: Mapped[str] = mapped_column(String(255))
    """str: 用户所在的地区。"""

    qq_uid: Mapped[int] = mapped_column(String(30), nullable=False, primary_key=True)
    """int: 用户的QQ uid。"""

    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())
    """DateTime: 用户信息的更新时间。"""

    # group_id: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<User(puuid='{self.puuid}', cookie='{self.cookie}', access_token='{self.access_token}', token_id='{self.token_id}', emt='{self.emt}', username='{self.username}', region='{self.region}', expiry_token='{self.expiry_token}', qq_uid='{self.qq_uid}', timestamp='{self.timestamp}')>"


class WeaponSkin(BaseModel):
    """武器皮肤模型类

    该模型表示一种武器皮肤，包含唯一标识符、名称、图标和级别四个属性。
    """

    __tablename__ = "weapon_skins"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    """str: 武器皮肤的唯一标识符，作为主键。"""

    names: Mapped[JSON] = mapped_column(JSON)
    """JSON: 武器皮肤的名称。"""

    icon: Mapped[str] = mapped_column(String(255))
    """str: 武器皮肤的图标。"""

    tier: Mapped[str] = mapped_column(String(255))
    """str: 武器皮肤的级别。"""

    def __repr__(self):
        return f"<WeaponSkin(uuid='{self.uuid}', names='{self.names}', icon='{self.icon}', tier='{self.tier}')>"


class Version(BaseModel):
    __tablename__ = "version"
    """
        "manifestId": "4CDFEE53A361DD60",
        "branch": "release-06.08",
        "version": "06.08.00.875485",
        "buildVersion": "19",
        "engineVersion": "4.26.2.0",
        "riotClientVersion": "release-06.08-shipping-19-875485",
        "riotClientBuild": "65.0.2.5073401.749",
        "buildDate": "2023-05-04T00:00:00Z",
    """

    manifestId: Mapped[str] = mapped_column(String(255), primary_key=True)
    """str: 游戏版本的manifestId。"""

    branch: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的branch。"""

    version: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的version。"""

    buildVersion: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的buildVersion。"""

    engineVersion: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的engineVersion。"""

    riotClientVersion: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的riotClientVersion。"""

    riotClientBuild: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的riotClientBuild。"""

    buildDate: Mapped[str] = mapped_column(String(255))
    """str: 游戏版本的buildDate。"""

    def __repr__(self):
        return f"<Version(uuid='{self.uuid}', manifestId='{self.manifestId}', branch='{self.branch}', version='{self.version}', buildVersion='{self.buildVersion}', engineVersion='{self.engineVersion}', riotClientVersion='{self.riotClientVersion}', riotClientBuild='{self.riotClientBuild}', buildDate='{self.buildDate}')>"


class Tier(BaseModel):
    __tablename__ = "tier"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[int] = mapped_column(String(255))

    icon: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Tier(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"


class Mission(BaseModel):
    __tablename__ = "mission"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    titles: Mapped[str] = mapped_column(String(255))

    type: Mapped[str] = mapped_column(String(255))

    progress: Mapped[str] = mapped_column(String(255))

    xp: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Mission(uuid='{self.uuid}', titles='{self.titles}', type='{self.type}', progress='{self.progress}', xp='{self.xp}')>"


class Playercard(BaseModel):
    __tablename__ = "playercard"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    icon: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return (
            f"<Playercard(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"
        )


class Title(BaseModel):
    __tablename__ = "title"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    name: Mapped[str] = mapped_column(String(255))

    text: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<Title(uuid='{self.uuid}', name='{self.name}', icon='{self.text}')>"
