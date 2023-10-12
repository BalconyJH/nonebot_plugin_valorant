from typing import Optional

from pydantic import BaseModel

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.config import plugin_config


class Skin(BaseModel):
    uuid: str
    name: str
    icon: str
    cost: int
    currency: str
    startdate: str


class SkinsPanel(BaseModel):
    skin1: Optional[Skin]
    skin2: Optional[Skin]
    skin3: Optional[Skin]
    skin4: Optional[Skin]
    duration: int


async def skin_panel_parser(data):
    """
    Parse raw data from endpoint.
    """
    try:
        uuids = data["SkinsPanelLayout"]["SingleItemOffers"]
        duration = data["SkinsPanelLayout"][
            "SingleItemOffersRemainingDurationInSeconds"
        ]
        skins_panel = SkinsPanel(duration=duration)
        for index, uuid in enumerate(uuids):
            currency, cost = list(
                data["SkinsPanelLayout"]["SingleItemStoreOffers"][index]["Cost"].items()
            )[0]
            startdate = data["SkinsPanelLayout"]["SingleItemStoreOffers"][index][
                "StartDate"
            ]
            skin_data = await DB.get_skin(uuid)
            skin = Skin(
                uuid=uuid,
                name=skin_data.names[plugin_config.language_type],
                icon=skin_data.icon,
                cost=cost,
                currency=currency,
                startdate=startdate,
            )
            setattr(skins_panel, f"skin{index+1}", skin)
        return skins_panel
    except IndexError as e:
        raise ValueError(f"Invalid data: {e}") from e
