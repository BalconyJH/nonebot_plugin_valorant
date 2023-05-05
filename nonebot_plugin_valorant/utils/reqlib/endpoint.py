# inspired by https://github.com/colinhartigan/

from __future__ import annotations

import contextlib
# Standard
import json
from typing import Any, Dict, Mapping, Optional

import requests
import urllib3

from nonebot_plugin_valorant.utils.errors import HandshakeError, ResponseError

# Local
from nonebot_plugin_valorant.utils.reqlib.request_res import (base_endpoint,
                                                              base_endpoint_glz,
                                                              base_endpoint_shared,
                                                              region_shard_override,
                                                              shard_region_override)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EndpointAPI:
    def __init__(self, auth: Mapping[str, Any]) -> None:
        from .auth import Auth

        self.auth = Auth()

        try:
            self.headers = self.__build_headers(auth['headers'])
            self.puuid = auth['puuid']
            self.region = auth['region']
            self.player = auth['player_name']
            self.locale_code = auth.get('locale_code', 'en-US')
            self.__format_region()
            self.__build_urls()
        except Exception as e:
            raise HandshakeError("errors.API.FAILED_ACTIVE") from e

        # client platform
        self.client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'

        # language
        self.locale_code = 'en-US'

    # async def refresh_token(self) -> None:
    # cookies = self.cookie
    # cookies, accessToken, emt = await self.auth.redeem_cookies(cookies)

    # self.__build_headers()

    def fetch(self, endpoint: str = '/', url: str = 'pd') -> Dict:
        """fetch data from the api"""

        endpoint_url = getattr(self, url)

        r = requests.get(f'{endpoint_url}{endpoint}', headers=self.headers)

        with contextlib.suppress(Exception):
            data = json.loads(r.text)
        if "httpStatus" not in data:
            return data

        if data["httpStatus"] == 400:
            raise ResponseError("errors.AUTH.COOKIES_EXPIRED")
            # await self.refresh_token()
            # return await self.fetch(endpoint=endpoint, url=url, errors=errors)

    def put(self, endpoint: str = "/", url: str = "pd", data: dict = None) -> dict:
        """
        发送 PUT 请求到 API。

        Args:
            endpoint: API 的路径，默认为根路径。
            url: API 的 URL 名称，默认为 pd。
            data: 发送到 API 的数据。

        Returns:
            返回 API 的响应结果。

        Raises:
            ResponseError: 如果 API 返回的响应结果为空，则抛出异常。
        """

        if data is None:
            data = {}

        endpoint_url = getattr(self, url)

        r = requests.put(f"{endpoint_url}{endpoint}", headers=self.headers, json=data)
        r.raise_for_status()

        data = r.json()

        if data is not None:
            return data
        else:
            raise ResponseError("errors.API.REQUEST_FAILED")

    # contracts endpoints

    def fetch_contracts(self) -> Mapping[str, Any]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.fetch(endpoint=f'/contracts/v1/contracts/{self.puuid}', url='pd')

    # PVP endpoints

    def fetch_content(self) -> Mapping[str, Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.fetch(endpoint='/content-service/v3/content', url='shared')

    def fetch_account_xp(self) -> Mapping[str, Any]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.fetch(endpoint=f'/account-xp/v1/players/{self.puuid}', url='pd')

    def fetch_player_mmr(self, puuid: str = None) -> Mapping[str, Any]:
        puuid = self.__check_puuid(puuid)
        return self.fetch(endpoint=f'/mmr/v1/players/{puuid}', url='pd')

    def fetch_name_by_puuid(self, puuid: str = None) -> Mapping[str, Any]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """
        if puuid is None:
            puuid = [self.__check_puuid()]
        elif type(puuid) is str:
            puuid = [puuid]
        return self.put(endpoint='/name-service/v2/players', url='pd', body=puuid)

    def fetch_player_loadout(self) -> Mapping[str, Any]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        return self.fetch(
            endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout',
            url='pd',
        )

    def put_player_loadout(self, loadout: Mapping) -> Mapping[str, Any]:
        """
        playerLoadoutUpdate
        Use the values from `fetch_player_loadout` excluding properties like `subject` and `version.` Loadout changes take effect when starting a new game
        """
        return self.put(
            endpoint=f'/personalization/v2/players/{self.puuid}/playerloadout',
            url='pd',
            body=loadout,
        )

    # store endpoints

    def store_fetch_offers(self) -> Mapping[str, Any]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        return self.fetch('/store/v1/offers/', url='pd')

    def store_fetch_storefront(self) -> Mapping[str, Any]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        return self.fetch(f'/store/v2/storefront/{self.puuid}', url='pd')

    def store_fetch_wallet(self) -> Mapping[str, Any]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radiant points the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741 and Radiant points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        return self.fetch(f'/store/v1/wallet/{self.puuid}', url='pd')

    def store_fetch_order(self, order_id: str) -> Mapping[str, Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.fetch(f'/store/v1/order/{order_id}', url='pd')

    def store_fetch_entitlements(self, item_type: Mapping) -> Mapping[str, Any]:
        """
        Store_GetEntitlements
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in `fetch_content` to know what items are owned.
        Category names and IDs:

        `ITEMTYPEID:`
        '01bb38e1-da47-4e6a-9b3d-945fe4655707': 'Agents'\n
        'f85cb6f7-33e5-4dc8-b609-ec7212301948': 'Contracts',\n
        'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475': 'Sprays',\n
        'dd3bf334-87f3-40bd-b043-682a57a8dc3a': 'Gun Buddies',\n
        '3f296c07-64c3-494c-923b-fe692a4fa1bd': 'Player Cards',\n
        'e7c63390-eda7-46e0-bb7a-a6abdacd2433': 'Skins',\n
        '3ad1b2b2-acdb-4524-852f-954a76ddae0a': 'Skins chroma',\n
        'de7caa6b-adf7-4588-bbd1-143831e786c6': 'Player titles',\n
        """
        return self.fetch(
            endpoint=f"/store/v1/entitlements/{self.puuid}/{item_type}", url="pd"
        )

    # useful endpoints

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
        return self.fetch_account_xp()['Progress']['Level']

    def get_player_tier_rank(self, puuid: str = None) -> str:
        """
        get player current tier rank
        """
        data = self.fetch_player_mmr(puuid)
        season_id = data['LatestCompetitiveUpdate']['SeasonID']
        if len(season_id) == 0:
            season_id = self.__get_live_season()
        current_season = data["QueueSkills"]['competitive']['SeasonalInfoBySeasonID']
        return current_season[season_id]['CompetitiveTier']

    # local utility functions

    def __get_live_season(self) -> str:
        """Get the UUID of the live competitive season"""
        content = self.fetch_content()
        season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
        return (
            season_id[0]
            if season_id
            else self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
        )

    def __check_puuid(self, puuid: Optional[str] = None) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self.puuid if puuid is None else puuid

    def __build_urls(self):
        """
        generate URLs based on region/shard
        """
        self.pd = base_endpoint.format(shard=self.shard)
        self.shared = base_endpoint_shared.format(shard=self.shard)
        self.glz = base_endpoint_glz.format(region=self.region, shard=self.shard)

    def __build_headers(self, headers) -> Mapping[str, Any]:
        """build headers"""

        headers['X-Riot-ClientPlatform'] = self.client_platform
        headers['X-Riot-ClientVersion'] = self._get_client_version()
        return headers

    def __format_region(self) -> None:
        """Format region to match from user input"""

        self.shard = self.region
        if self.region in region_shard_override.keys():
            self.shard = region_shard_override[self.region]
        if self.shard in shard_region_override.keys():
            self.region = shard_region_override[self.shard]

    @staticmethod
    def _get_client_version() -> str:
        """
        获取 Valorant 客户端版本信息

        Returns:
            str: 客户端版本信息，格式为 "<分支>-shipping-<构建版本>-<第四位版本号>"
        """
        r = requests.get('https://valorant-api.com/v1/version')
        data = r.json()['data']
        return f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"  # return formatted version string

    @staticmethod
    def get_valorant_version():
        """获取VALORANT版本号

        Returns:
            str: VALORANT版本号，如果获取失败则返回None
        """
        r = requests.get('https://valorant-api.com/v1/version')
        if r.status_code != 200:
            return None
        data = r.json()['data']
        return data['version']
