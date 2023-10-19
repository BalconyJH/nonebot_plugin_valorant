from sqlalchemy.orm import Mapped, Session, relationship, declarative_base
from sqlalchemy import (
    JSON,
    BIGINT,
    INTEGER,
    VARCHAR,
    Column,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)

Base = declarative_base()

# association_table = Table(
#     ""
# )


class BaseModel(Base):
    """
    This class is the base model for all other models in the project. It provides common methods for querying, adding, deleting, and updating data in the database.

    Attributes:
        __abstract__ (bool): True if this is an abstract class, False otherwise.

    Methods:
        get(cls, session: Session, **kwargs):
            Retrieve a list of instances of the model that match the provided keyword arguments.

        add(cls, session: Session, **kwargs):
            Create a new instance of the model with the provided keyword arguments and add it to the session.

        delete(cls, session: Session, **kwargs) -> bool:
            Delete the instance(s) of the model that match the provided keyword arguments.

        update(cls, q, **kwargs) -> bool:
            Update the instance(s) of the model that match the provided query and keyword arguments.

    Note:
        - This class does not have a constructor (__init__) as it is an abstract class.
        - The methods in this class are asynchronous.

    Example usage:

        # Get instance(s)
        instances = await BaseModel.get(session, name='John')

        # Add new instance
        await BaseModel.add(session, name='John', age=30)

        # Delete instance(s)
        deleted = await BaseModel.delete(session, age=30)

        # Update instance(s)
        updated = await BaseModel.update(session, {'name': 'John'}, age=40)
    """

    __abstract__ = True

    @classmethod
    async def get(cls, session: Session, *args, **kwargs):
        if args:
            query = session.query(*args)
        else:
            query = session.query(cls)

        if kwargs:
            query = query.filter_by(**kwargs)

        return query

    @classmethod
    async def add(cls, session: Session, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()

    @classmethod
    async def delete(cls, session: Session, **kwargs) -> bool:
        query = session.query(cls).filter_by(**kwargs).first()
        if query is not None:
            session.delete(query)
            session.commit()
            return True
        return False

    @classmethod
    async def update(cls, session: Session, filter_by: dict, update_values: dict):
        query = session.query(cls).filter_by(**filter_by)
        query.update(update_values)
        session.commit()

    # @classmethod
    # async def get_all(cls, session: Session, *args):
    #     return session.query(cls, *args).all()


# class FeaturedBundle:
#     __tablename__ = "featured_bundle"


# class UpgradeCurrencyStore:
#     __tablename__ = "upgrade_currency_store"


class AccessoryStore(BaseModel):
    """
    This class represents an accessory store entry in the database.

    Attributes:
        uuid (str): The unique identifier of the player.
        offer_id (str): The ID of the offer.
        cost_type (str): The currency type used for the cost.
        cost (str): The price of the accessory.
        remaining_duration (str): The remaining duration of the accessory.

    """

    __tablename__ = "accessory_store"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    offer_id: Mapped[str] = Column(VARCHAR(255))
    cost_type: Mapped[str] = Column(VARCHAR(255))
    cost: Mapped[str] = Column(VARCHAR(255))
    remaining_duration: Mapped[str] = Column(VARCHAR(255))


class SkinsStore(BaseModel):
    """
    This class represents a skins store entry in the database.

    Attributes:
        puuid (str): Player UUID.
        offer_1 (str): Currency offer ID 1.
        offer_2 (str): Currency offer ID 2.
        offer_3 (str): Currency offer ID 3.
        offer_4 (str): Currency offer ID 4.
        duration (inT): Duration of the store.
        timestamp (datetime): Timestamp of the store.
    """

    __tablename__ = "skins_store"

    puuid = Column(VARCHAR(36), primary_key=True)
    offer_1 = Column(VARCHAR(36))
    offer_2 = Column(VARCHAR(36))
    offer_3 = Column(VARCHAR(36))
    offer_4 = Column(VARCHAR(36))
    duration = Column(BIGINT)
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="skins_store")

    def __repr__(self):
        return f"<SkinsStore(puuid='{self.puuid}', offer_1='{self.offer_1}', offer_2='{self.offer_2}', offer_3='{self.offer_3}', offer_4='{self.offer_4}', duration='{self.duration}', timestamp='{self.timestamp}')>"


class BonusStore(BaseModel):
    """
    Class representing a Bonus Store.

    Attributes:
        uuid (str): The UUID of the player.
        offer_id (str): The ID of the currency offer.
        cost_type (str): The currency type.
        cost (str): The price of the currency.
        discount (str): The currency discount.
        discount_cost (str): The price of the currency after discount.
        remaining_duration (str): The remaining duration.

    """

    __tablename__ = "bonus_store"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    offer_id: Mapped[str] = Column(VARCHAR(255))
    cost_type: Mapped[str] = Column(VARCHAR(255))
    cost: Mapped[str] = Column(VARCHAR(255))
    discount: Mapped[str] = Column(VARCHAR(255))
    discount_cost: Mapped[str] = Column(VARCHAR(255))
    remaining_duration: Mapped[str] = Column(VARCHAR(255))


class User(BaseModel):
    """ """

    __tablename__ = "user"

    # 平台用户唯一标识
    qq_uid = Column(VARCHAR(30), nullable=False, unique=True)

    # Riot用户信息
    puuid = Column(VARCHAR(36), ForeignKey("skins_store.puuid"), primary_key=True)
    cookie = Column(JSON)
    access_token = Column(VARCHAR(2000))
    token_id = Column(VARCHAR(2000))
    expiry_token = Column(BIGINT)
    emt = Column(VARCHAR(2000))
    username = Column(VARCHAR(255))
    region = Column(VARCHAR(255))
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    skins_store = relationship("SkinsStore", back_populates="user")

    def __repr__(self):
        return f"<User(qq_uid='{self.qq_uid}', puuid='{self.puuid}', cookie='{self.cookie}', access_token='{self.access_token}', token_id='{self.token_id}', expiry_token='{self.expiry_token}', emt='{self.emt}', username='{self.username}', region='{self.region}', timestamp='{self.timestamp}')>"


class WeaponSkins(BaseModel):
    """
    This class represents a weapon skins in the database.

    Attributes:
        uuid (str): The unique identifier for the weapon skins, used as the primary key.
        names (JSON): The names of the weapon skins.
        icon (str): The icon of the weapon skins.
        tier (str): The tier of the weapon skins.
        hash (str): The hash value of the weapon skins resource.

    """

    __tablename__ = "weapon_skins"

    uuid = Column(VARCHAR(255), primary_key=True)
    names = Column(JSON)
    icon = Column(VARCHAR(255))
    tier = Column(VARCHAR(255))
    hash = Column(VARCHAR(255))

    def __repr__(self):
        return f"<WeaponSkins(uuid='{self.uuid}', names='{self.names}', icon='{self.icon}', tier='{self.tier}', hash='{self.hash}')>"


class Version(BaseModel):
    """
    A class representing the Version table in a database.

    Attributes:
        manifestId (str): The primary key of the table, representing the manifest id.
        branch (str): The branch of the version.
        version (str): The version of the application.
        buildVersion (str): The build version of the application.
        engineVersion (str): The engine version of the application.
        riotClientVersion (str): The Riot client version of the application.
        riotClientBuild (str): The Riot client build of the application.
        buildDate (str): The build date of the application.

    """

    __tablename__ = "version"

    manifestId = Column(VARCHAR(255), primary_key=True)
    branch = Column(VARCHAR(255))
    version = Column(VARCHAR(255))
    buildVersion = Column(VARCHAR(255))
    engineVersion = Column(VARCHAR(255))
    riotClientVersion = Column(VARCHAR(255))
    riotClientBuild = Column(VARCHAR(255))
    buildDate = Column(VARCHAR(255))
    initial = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Version('manifestId='{self.manifestId}', branch='{self.branch}', version='{self.version}', buildVersion='{self.buildVersion}', engineVersion='{self.engineVersion}', riotClientVersion='{self.riotClientVersion}', riotClientBuild='{self.riotClientBuild}', buildDate='{self.buildDate}', initial='{self.initial}')>"


class Tier(BaseModel):
    """
    Class representing a Tier entity.

    Attributes:
        uuid (str): The unique identifier of the Tier.
        name (str): The name of the Tier.
        icon (str): The icon associated with the Tier.


    Example:
        tier = Tier(uuid='123', name='Tier 1', icon='icon.png')

    Note:
        This class is a subclass of BaseModel.
    """

    __tablename__ = "tier"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    name: Mapped[str] = Column(VARCHAR(255))
    icon: Mapped[str] = Column(VARCHAR(255))

    def __repr__(self):
        return f"<Tier(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"


class Mission(BaseModel):
    """
    Represents a mission entity.

    Attributes:
        uuid (str): The unique identifier of the mission.
        titles (str): The titles associated with the mission.
        type (str): The type of the mission.
        progress (str): The progress of the mission.
        xp (str): The experience poInts gained from the mission.
    """

    __tablename__ = "mission"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    titles: Mapped[str] = Column(VARCHAR(255))
    type: Mapped[str] = Column(VARCHAR(255))
    progress: Mapped[str] = Column(VARCHAR(255))
    xp: Mapped[str] = Column(VARCHAR(255))

    def __repr__(self):
        return f"<Mission(uuid='{self.uuid}', titles='{self.titles}', type='{self.type}', progress='{self.progress}', xp='{self.xp}')>"


class Playercard(BaseModel):
    """
    Represents a player card in the game.

    Attributes:
        uuid (str): The unique identifier of the player card.
        name (str): The name of the player card.
        icon (str): The icon associated with the player card.
    """

    __tablename__ = "playercard"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    name: Mapped[str] = Column(VARCHAR(255))
    icon: Mapped[str] = Column(VARCHAR(255))

    def __repr__(self):
        return (
            f"<Playercard(uuid='{self.uuid}', name='{self.name}', icon='{self.icon}')>"
        )


class Title(BaseModel):
    """
    This class represents a Title in the database.

    Attributes:
        uuid (str): The UUID of the Title (primary key).
        name (str): The name of the Title.
        text (str): The text content of the Title.


    Example Usage:
        title = Title(uuid='123456789', name='Example Title', text='Lorem ipsum')
    """

    __tablename__ = "title"

    uuid: Mapped[str] = Column(VARCHAR(255), primary_key=True)
    name: Mapped[str] = Column(VARCHAR(255))
    text: Mapped[str] = Column(VARCHAR(255))

    def __repr__(self):
        return f"<Title(uuid='{self.uuid}', name='{self.name}', icon='{self.text}')>"
