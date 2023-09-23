from typing import Any, Dict, Mapping, Optional

import urllib3

from nonebot_plugin_valorant.utils import message_translator
from nonebot_plugin_valorant.utils.errors import HandshakeError
from nonebot_plugin_valorant.utils.reqlib.auth import AuthCredentials
from nonebot_plugin_valorant.utils.reqlib.client import get_client_version
from nonebot_plugin_valorant.utils.reqlib.player_info import PlayerInformation
from nonebot_plugin_valorant.utils.reqlib.request_res import (
    base_endpoint,
    get_request_json,
    put_request_json,
    base_endpoint_glz,
    base_endpoint_shared,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EndpointAPI:
    def __init__(self, player_info: PlayerInformation) -> None:
        """
        传入AuthCredentials初始化API
        Args:
            auth:
        """
        from .auth import Auth

        self.auth = Auth()
        # client platform 神秘参数,我也不知道哪来的
        # noinspection SpellCheckingInspection
        self.client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

        # language
        self.locale_code = "en-US"

        self.headers = self.__build_headers(self.auth.headers)
        self.puuid = player_info.puuid
        self.region = player_info.region
        self.player_name = player_info.player_name
        self.__format_region()
        self.__build_urls()

    def __build_headers(self, headers) -> Dict[str, Any]:
        """build headers"""

        headers["X-Riot-ClientPlatform"] = self.client_platform
        headers["X-Riot-ClientVersion"] = get_client_version()
        return headers

    def __format_region(self):
        """
        将地区格式化为符合要求的格式
        """

        region_shard_override = {
            "latam": "na",
            "br": "na",
        }

        shard_region_override = {"pbe": "na"}

        self.shard = self.region

        if self.region in region_shard_override:
            self.shard = region_shard_override[self.region]

        if self.shard in shard_region_override:
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

    async def fetch(self, api_path: str = "/", api_url: str = "pd") -> Dict:
        """
        从 API 获取数据。

        Args:
            api_path (str): API 的路径，默认为根路径。
            api_url (str): API 的 URL 名称，默认为 pd。

        Returns:
            Dict: 返回获取到的数据。

        Raises:
            ResponseError: 如果 API 返回的响应结果为空，则抛出异常。
        """
        api_endpoint = getattr(self, api_url)

        data = await get_request_json(f"{api_endpoint}{api_path}", headers=self.headers)

        if data["status_code"] == 400:
            raise HandshakeError("errors.AUTH.COOKIES_EXPIRED")

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
        data = await put_request_json(
            url=f"{endpoint_url}{endpoint}", data=data, headers=self.headers
        )
        return data

    async def fetch_contracts(self) -> Mapping[str, Any]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return await self.fetch(f"/contracts/v1/contracts/{self.puuid}", "pd")

    async def fetch_content(self) -> Mapping[str, Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return await self.fetch("/content-service/v3/content", "shared")

    async def fetch_account_xp(self) -> Mapping[str, Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return await self.fetch(f"/account-xp/v1/players/{self.puuid}", "pd")

    async def fetch_player_mmr(self, puuid: str) -> Mapping[str, Any]:
        puuid = await self.__check_puuid(puuid)
        return await self.fetch(f"/mmr/v1/players/{puuid}", "pd")

    # store endpoints

    async def fetch_name_by_puuid(self, puuid: str) -> dict:
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
            puuid = await self.__check_puuid()
        elif isinstance(puuid, str):
            puuid = puuid
        return await self.put(endpoint="/name-service/v2/players", url="pd", data=puuid)

    async def fetch_player_loadout(self) -> dict:
        # noinspection SpellCheckingInspection
        """
        playerLoadoutUpdate
        获取玩家当前的装备设置。

        Returns:
            dict: 包含玩家当前装备设置的响应结果。
        """
        return await self.put(
            endpoint=f"/personalization/v2/players/{self.puuid}/playerloadout",
            url="pd",
        )

    async def put_player_loadout(self, loadout: dict) -> dict:
        """
        playerLoadoutUpdate
        使用从 `fetch_player_loadout` 获取的值（不包括 `subject` 和 `version` 等属性）来更新装备设置。
        装备设置将在开始新游戏时生效。

        Args:
            loadout: 要更新的装备设置数据。

        Returns:
            dict: 包含更新后装备设置的响应结果。
        """
        return await self.put(
            endpoint=f"/personalization/v2/players/{self.puuid}/playerloadout",
            url="pd",
            data=loadout,
        )

    async def get_offers(self) -> Mapping[str, Any]:
        """
        获取商店中所有商品的价格信息。
        """
        return await self.fetch("/store/v1/offers/", "pd")

    async def get_player_storefront(self) -> Mapping[str, Any]:
        """
        获取玩家商店中当前可用的商品。

        Returns:
            FeaturedBundle: 特色捆绑包
            SkinsPanelLayout： 武器皮肤
            UpgradeCurrencyStore: 升级货币商店
            BonusStore: 夜市
            AccessoryStore: 附件商店

            "httpStatus": 400 验证/解码 RSO 访问令牌失败

        """
        return await self.fetch(f"/store/v2/storefront/{self.puuid}", "pd")

    async def get_player_wallet(self) -> Mapping[str, Any]:
        """
        获取玩家钱包中的 Valorant 点数和 Radiant 点数余额。

        Valorant 点数的 ID 为 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741。
        Radiant 点数的 ID 为 e59aa87c-4cbf-517a-5983-6e81511be9b7。
        未知货币的 ID 为 f08d4ae3-939c-4576-ab26-09ce1f23bb37。

        Returns:
            包含玩家钱包中 Valorant 点数和 Radiant 点数余额的字典。
        """
        return await self.fetch(f"/store/v1/wallet/{self.puuid}", "pd")

    async def store_fetch_order(self, order_id: str) -> Mapping[str, Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return await self.fetch(f"/store/v1/order/{order_id}", "pd")

    async def store_fetch_entitlements(self, item_type: Mapping) -> Mapping[str, Any]:
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
        return await self.fetch(
            f"/store/v1/entitlements/{self.puuid}/{item_type}", "pd"
        )

    # local utility functions

    async def fetch_mission(self) -> Mapping[str, Any]:
        """
        Get player daily/weekly missions
        """
        data = await self.fetch_contracts()
        return data["Missions"]

    async def get_player_level(self) -> Mapping[str, Any]:
        """
        Aliases `fetch_account_xp` but received a level
        """
        data = await self.fetch_account_xp()
        return data["Progress"]["Level"]

    async def get_player_tier_rank(self, puuid: str) -> str:
        """
        get player current tier rank
        """
        data = await self.fetch_player_mmr(puuid)
        season_id = data["LatestCompetitiveUpdate"]["SeasonID"]
        if len(season_id) == 0:
            season_id = await self.__get_live_season(puuid)
        current_season = data["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]
        return current_season[season_id]["CompetitiveTier"]

    async def __get_live_season(self, puuid: str) -> str:
        """Get the UUID of the live competitive season"""
        content = await self.fetch_content()
        season_id = [
            season["ID"]
            for season in content["Seasons"]
            if season["IsActive"] and season["Type"] == "act"
        ]
        return (
            season_id[0]
            if season_id
            else (await self.fetch_player_mmr(puuid))["LatestCompetitiveUpdate"][
                "SeasonID"
            ]
        )

    async def __check_puuid(self, puuid: Optional[str] = None) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid
