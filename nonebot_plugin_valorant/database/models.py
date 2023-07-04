from sqlalchemy import JSON, Column, DateTime, String, Text, func

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    Session,
    declarative_base,
    relationship,
)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    async def get(cls, session: Session, **kwargs):
        return session.query(cls).filter_by(**kwargs)

    @classmethod
    async def add(cls, session: Session, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()

    @classmethod
    async def delete(cls, session: Session, **kwargs) -> bool:
        query = await cls.get(session, **kwargs)
        if query.count():
            query.delete()
            session.commit()
            return True
        return False

    @classmethod
    async def update(cls, q, **kwargs) -> bool:
        query = await cls.get(**q)
        if await query.exists():
            query.update(**kwargs)
            return True
        return False

    # @classmethod
    # def matches_data(cls, data: Dict) -> bool:
    #     """
    #     检查数据UUID是否与模型匹配。
    #     :param
    #     - data:["uuid"]
    #     :return:
    #     - bool: 数据UUID与模型匹配返回True，否则返回False。
    #     """
    #     # return data.get("uuid") == str(cls.uuid)

    #     # TODO: 检查数据是否匹配, 添加读取数据库uuid比对

    # @classmethod
    # def merge(cls, session, **kwargs):
    #     query = cls.get(session, uuid=kwargs["uuid"])
    #     if query.count():
    #         query.update(kwargs)
    #         session.commit()
    #     else:
    #         cls.add(session, **kwargs)


class UserShop(BaseModel):
    """
    用户商店类。

    :ivar uuid: 玩家UUID。
    :vartype uuid: str

    :ivar bonus_store: 夜市。
    :vartype bonus_store: BonusStore

    :ivar skins_store: 皮肤商店。
    :vartype skins_store: SkinsStore

    :ivar accessory_store: 配件商店。
    :vartype accessory_store: AccessoryStore

    # :ivar featured_bundle: 特色捆绑包。
    # :vartype featured_bundle: FeaturedBundle
    #
    # :ivar upgrade_currency_store: 升级货币商店。
    # :vartype upgrade_currency_store: UpgradeCurrencyStore
    """

    __tablename__ = "user_shop"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)

    bonus_store: Mapped["BonusStore"] = relationship("BonusStore", backref="user_shop", primaryjoin="UserShop.uuid == foreign(BonusStore.uuid)")
    skins_store: Mapped["SkinsStore"] = relationship("SkinsStore", backref="user_shop", primaryjoin="UserShop.uuid == foreign(SkinsStore.uuid)")
    accessory_store: Mapped["AccessoryStore"] = relationship(
        "AccessoryStore", backref="user_shop",
        primaryjoin="UserShop.uuid == foreign(AccessoryStore.uuid)"
    )


#     featured_bundle: "FeaturedBundle" = relationship(
#         "FeaturedBundle", backref="user_shop"
#     )
#     upgrade_currency_store: "UpgradeCurrencyStore" = relationship(
#         "UpgradeCurrencyStore", backref="user_shop"
#     )


# class FeaturedBundle:
#     __tablename__ = "featured_bundle"


# class UpgradeCurrencyStore:
#     __tablename__ = "upgrade_currency_store"


class AccessoryStore(BaseModel):
    """
    配件商店类。

    :ivar uuid: 玩家UUID。
    :vartype uuid: str

    :ivar offer_id: 配件商店的优惠 ID。
    :vartype offer_id: str

    :ivar cost_type: 配件商店的消费类型。
    :vartype cost_type: str

    :ivar cost: 配件商店的价格。
    :vartype cost: str

    :ivar remaining_duration: 配件商店的剩余持续时间。
    :vartype remaining_duration: str
    """

    __tablename__ = "accessory_store"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(255))
    cost_type: Mapped[str] = mapped_column(String(255))
    cost: Mapped[str] = mapped_column(String(255))
    remaining_duration: Mapped[str] = mapped_column(String(255))


class SkinsStore(BaseModel):
    """
    皮肤商店类。


    :ivar uuid: 玩家UUID。
    :vartype uuid: str

    :ivar offer_id_1: 皮肤商店的优惠 ID 1。
    :vartype offer_id_1: str

    :ivar offer_id_2: 皮肤商店的优惠 ID 2。
    :vartype offer_id_2: str

    :ivar offer_id_3: 皮肤商店的优惠 ID 3。
    :vartype offer_id_3: str

    :ivar offer_id_4: 皮肤商店的优惠 ID 4。
    :vartype offer_id_4: str
    """

    __tablename__ = "skins_store"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    offer_id_1: Mapped[str] = mapped_column(String(255))
    offer_id_2: Mapped[str] = mapped_column(String(255))
    offer_id_3: Mapped[str] = mapped_column(String(255))
    offer_id_4: Mapped[str] = mapped_column(String(255))


class BonusStore(BaseModel):
    """
    夜市类。

    :ivar uuid: 夜市的 UUID。
    :vartype uuid: str

    :ivar offer_id: 夜市的优惠 ID。
    :vartype offer_id: str

    :ivar cost_type: 夜市的消费类型。
    :vartype cost_type: str

    :ivar cost: 夜市的价格。
    :vartype cost: str

    :ivar discount: 夜市的折扣。
    :vartype discount: str

    :ivar discount_cost: 夜市的折扣价格。
    :vartype discount_cost: str

    :ivar remaining_duration: 夜市的剩余持续时间。
    :vartype remaining_duration: str
    """

    __tablename__ = "bonus_store"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(255))
    cost_type: Mapped[str] = mapped_column(String(255))
    cost: Mapped[str] = mapped_column(String(255))
    discount: Mapped[str] = mapped_column(String(255))
    discount_cost: Mapped[str] = mapped_column(String(255))
    remaining_duration: Mapped[str] = mapped_column(String(255))


class User(BaseModel):
    """
    用户类。

    该模型表示一个用户，包含了用户的各种信息，例如唯一标识符、cookie、access token等。


    :ivar puuid: 用户的唯一标识符。
    :vartype puuid: str

    :ivar cookie: 用户的 cookie。
    :vartype cookie: JSON

    :ivar access_token: 用户的 access token。
    :vartype access_token: Text

    :ivar token_id: 用户的 token id。
    :vartype token_id: Text

    :ivar emt: 用户的 entitlements_token。
    :vartype emt: Text

    :ivar username: 用户的用户名。
    :vartype username: str

    :ivar region: 用户所在的地区。
    :vartype region: str

    :ivar qq_uid: 用户的 QQ uid。
    :vartype qq_uid: int

    :ivar timestamp: 用户信息的更新时间。
    :vartype timestamp: DateTime
    """

    __tablename__ = "user"

    puuid: Mapped[str] = mapped_column(String(255))
    cookie: Mapped[JSON] = mapped_column(JSON)
    access_token: Mapped[Text] = mapped_column(Text)
    token_id: Mapped[Text] = mapped_column(Text)
    emt: Mapped[Text] = mapped_column(Text)
    username: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255))
    qq_uid: Mapped[int] = mapped_column(String(30), nullable=False, primary_key=True)
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(puuid='{self.puuid}', cookie='{self.cookie}', access_token='{self.access_token}', token_id='{self.token_id}', emt='{self.emt}', username='{self.username}', region='{self.region}', qq_uid='{self.qq_uid}', timestamp='{self.timestamp}')>"


class WeaponSkin(BaseModel):
    """
    武器皮肤类。


    :ivar uuid: 武器皮肤的唯一标识符，作为主键。
    :vartype uuid: str

    :ivar names: 武器皮肤的名称。
    :vartype names: JSON

    :ivar icon: 武器皮肤的图标。
    :vartype icon: str

    :ivar tier: 武器皮肤的级别。
    :vartype tier: str

    :ivar hash: 武器皮肤资源的哈希值。
    :vartype hash: str
    """

    __tablename__ = "weapon_skins"

    uuid: Mapped[str] = mapped_column(String(255), primary_key=True)
    names: Mapped[JSON] = mapped_column(JSON)
    icon: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(255))
    hash: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"<WeaponSkin(uuid='{self.uuid}', names='{self.names}', icon='{self.icon}', tier='{self.tier}', hash='{self.hash}')>"


class Version(BaseModel):
    """
    版本类。

    :ivar manifestId: 清单标识。
    :vartype manifestId: str

    :ivar branch: 分支。
    :vartype branch: str

    :ivar version: 版本。
    :vartype version: str

    :ivar buildVersion: 构建版本。
    :vartype buildVersion: str

    :ivar engineVersion: 引擎版本。
    :vartype engineVersion: str

    :ivar riotClientVersion: 拳头客户端版本。
    :vartype riotClientVersion: str

    :ivar riotClientBuild: 拳头客户端构建。
    :vartype riotClientBuild: str

    :ivar buildDate: 构建日期。
    :vartype buildDate: str
    """

    __tablename__ = "version"

    manifestId: Mapped[str] = mapped_column(String(255), primary_key=True)
    branch: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(255))
    buildVersion: Mapped[str] = mapped_column(String(255))
    engineVersion: Mapped[str] = mapped_column(String(255))
    riotClientVersion: Mapped[str] = mapped_column(String(255))
    riotClientBuild: Mapped[str] = mapped_column(String(255))
    buildDate: Mapped[str] = mapped_column(String(255))

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
