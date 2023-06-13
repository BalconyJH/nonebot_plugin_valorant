# inspired by https://github.com/colinhartigan/


# Standard
from typing import Any, Dict, Mapping, Optional

import urllib3

from nonebot_plugin_valorant.utils.errors import HandshakeError
from nonebot_plugin_valorant.utils.reqlib.client import get_client_version
# Local
from nonebot_plugin_valorant.utils.reqlib.request_res import (
    base_endpoint,
    base_endpoint_glz,
    base_endpoint_shared,
    get_request_json_data,
    put_request_json_data,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EndpointAPI:
    def __init__(self, auth: Mapping[str, Any]) -> None:
        from .auth import Auth

        self.auth = Auth()

        try:
            self.headers = self.__build_headers(auth["headers"])
            self.puuid = auth["puuid"]
            self.region = auth["region"]
            self.player = auth["player_name"]
            self.locale_code = auth.get("locale_code", "en-US")
            self.__format_region()
            self.__build_urls()
        except Exception as e:
            raise HandshakeError("errors.API.FAILED_ACTIVE") from e

        # client platform
        # noinspection SpellCheckingInspection
        self.client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

        # language
        self.locale_code = "en-US"

    async def fetch(self, endpoint: str = "/", url: str = "pd") -> Dict:
        """从 API 获取数据。

        Args:
            endpoint: API 的路径，默认为根路径。
            url: API 的 URL 名称，默认为 pd。

        Returns:
            返回获取到的数据。
        """
        endpoint_url = getattr(self, url)

        return await get_request_json_data(
            f"{endpoint_url}{endpoint}", headers=self.headers
        )

    async def put(
            self, endpoint: str = "/", url: str = "pd", data: [dict, list] = None
    ) -> dict:
        """
        异步发送 PUT 请求到 API。

        Args:
            endpoint: API 的路径，默认为根路径。
            url: API 的 URL 名称，默认为 pd。
            data: 发送到 API 的数据。

        Returns:
            返回 API 的响应结果。

        Raises:
            ResponseError: 如果 API 返回的响应结果为空，则抛出异常。
        """
        endpoint_url = getattr(self, url)
        data = await put_request_json_data(
            url=f"{endpoint_url}{endpoint}", data=data, headers=self.headers
        )
        return data

    # contracts endpoints

    def fetch_contracts(self) -> Mapping[str, Any]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.fetch(endpoint=f"/contracts/v1/contracts/{self.puuid}", url="pd")

    # PVP endpoints

    def fetch_content(self) -> Mapping[str, Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.fetch(endpoint="/content-service/v3/content", url="shared")

    def fetch_account_xp(self) -> Mapping[str, Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.fetch(endpoint=f"/account-xp/v1/players/{self.puuid}", url="pd")

    def fetch_player_mmr(self, puuid: str = None) -> Mapping[str, Any]:
        puuid = self.__check_puuid(puuid)
        return self.fetch(endpoint=f"/mmr/v1/players/{puuid}", url="pd")

    def fetch_name_by_puuid(self, puuid: str = None) -> dict:
        """
        Name_service
        根据 PUUID 获取玩家的名字标签。

        Args:
            puuid: 玩家的 PUUID。如果未提供，将使用与实例关联的 PUUID。

        Returns:
            dict: 包含玩家名字标签的响应结果。

        注意：
        响应结果的格式为 ['PUUID']。
        """
        if puuid is None:
            puuid = [self.__check_puuid()]
        elif isinstance(puuid, str):
            puuid = [puuid]
        return self.put(endpoint="/name-service/v2/players", url="pd", data=puuid)

    def fetch_player_loadout(self) -> dict:
        # noinspection SpellCheckingInspection
        """
                playerLoadoutUpdate
                获取玩家当前的装备设置。

                Returns:
                    dict: 包含玩家当前装备设置的响应结果。
                """
        return self.put(
            endpoint=f"/personalization/v2/players/{self.puuid}/playerloadout",
            url="pd",
        )

    def put_player_loadout(self, loadout: dict) -> dict:
        """
        playerLoadoutUpdate
        使用从 `fetch_player_loadout` 获取的值（不包括 `subject` 和 `version` 等属性）来更新装备设置。
        装备设置将在开始新游戏时生效。

        Args:
            loadout: 要更新的装备设置数据。

        Returns:
            dict: 包含更新后装备设置的响应结果。
        """
        return self.put(
            endpoint=f"/personalization/v2/players/{self.puuid}/playerloadout",
            url="pd",
            data=loadout,
        )

    # store endpoints

    def get_offers(self) -> Mapping[str, Any]:
        """
        获取商店中所有商品的价格信息。
        """
        return self.fetch("/store/v1/offers/", url="pd")

    def get_storefront(self) -> Mapping[str, Any]:
        """
        获取商店中当前可用的商品。
        """
        return self.fetch(f"/store/v2/storefront/{self.puuid}", url="pd")

    def get_player_wallet_balance(self) -> Mapping[str, Any]:
        """
        获取玩家钱包中的 Valorant 点数和 Radiant 点数余额。
        Valorant 点数的 ID 为 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741。
        Radiant 点数的 ID 为 e59aa87c-4cbf-517a-5983-6e81511be9b7。

        Returns:
            包含玩家钱包中 Valorant 点数和 Radiant 点数余额的字典。
        """
        return self.fetch(f"/store/v1/wallet/{self.puuid}", url="pd")

    def store_fetch_order(self, order_id: str) -> Mapping[str, Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.fetch(f"/store/v1/order/{order_id}", url="pd")

    def store_fetch_entitlements(self, item_type: Mapping) -> Mapping[str, Any]:
        # noinspection SpellCheckingInspection
        """Store_GetEntitlements
        获取玩家拥有的物品列表（特务、皮肤、挂饰）。
        通过与 fetch_content 中的 UUID 相关联，了解拥有的物品。
        类别名称和 ID：

        ITEMTYPEID:
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': '特务'\n
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': '契约',\n
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': '喷漆',\n
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': '枪挂饰',\n
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': '玩家卡片',\n
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': '皮肤',\n
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': '皮肤染色',\n
        'de7caa6b-adf7-4588-bbd1-143831e786c6': '玩家称号',\n
        """
        return self.fetch(
            endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}", url="pd"
        )

    def fetch_mission(self) -> Mapping[str, Any]:
        """
        Get player daily/weekly missions
        """
        data = self.fetch_contracts()
        return data["Missions"]

    def get_player_level(self) -> Mapping[str, Any]:
        """
        Aliases `fetch_account_xp` but received a level
        """
        return self.fetch_account_xp()["Progress"]["Level"]

    def get_player_tier_rank(self, puuid: str = None) -> str:
        """
        get player current tier rank
        """
        data = self.fetch_player_mmr(puuid)
        season_id = data["LatestCompetitiveUpdate"]["SeasonID"]
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]
        return current_season[season_id]["CompetitiveTier"]

    # local utility functions

    def __get_live_season(self) -> str:
        """Get the UUID of the live competitive season"""
        content = self.fetch_content()
        season_id = [
            season["ID"]
            for season in content["Seasons"]
            if season["IsActive"] and season["Type"] == "act"
        ]
        return (
            season_id[0]
            if season_id
            else self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
        )

    def __check_puuid(self, puuid: Optional[str] = None) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid

    def __format_region(self):
        """
        将地区格式化为符合要求的格式

        Returns:
            None
        """

        # 地区到分区的映射关系
        region_shard_override = {
            "latam": "na",
            "br": "na",
        }

        # 分区到地区的映射关系
        shard_region_override = {"pbe": "na"}

        # 将 self.shard 设置为 self.region 的初始值
        self.shard = self.region

        # 如果 self.region 在 region_shard_override 的键中
        if self.region in region_shard_override:
            # 将 self.shard 设置为对应的分区
            self.shard = region_shard_override[self.region]

        # 如果 self.shard 在 shard_region_override 的键中
        if self.shard in shard_region_override:
            # 将 self.region 设置为对应的地区
            self.region = shard_region_override[self.shard]

    def __build_urls(self):
        """
        根据地区/分区生成URL

        根据地区和分区生成相应的URL

        Args:
            None

        Returns:
            None
        """

        # 基于分区构建URL
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)

        # 基于地区和分区构建URL
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    def __build_headers(self, headers) -> Dict[str, Any]:
        """build headers"""

        headers["X-Riot-ClientPlatform"] = self.client_platform
        headers["X-Riot-ClientVersion"] = get_client_version()
        return headers
