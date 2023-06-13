import json
from typing import Optional, Dict, Any

import aiohttp
from nonebot import logger

from nonebot_plugin_valorant.config import plugin_config
from nonebot_plugin_valorant.database.db import calculate_hash
from nonebot_plugin_valorant.utils.errors import ResponseError, DataParseError
from nonebot_plugin_valorant.utils.translator import Translator

# ------------------- #
# credit https://github.com/colinhartigan/
base_url = "https://valorant-api.com/v1/"
base_endpoint = "https://pd.{shard}.a.pvp.net"
base_endpoint_glz = "https://glz-{region}-1.{shard}.a.pvp.net"
base_endpoint_shared = "https://shared.{shard}.a.pvp.net"

regions: list = ["na", "eu", "latam", "br", "ap", "kr", "pbe"]

# ------------------- #


# EMOJI

emoji_icon_assests = {
    "DeluxeTier": "https://media.valorant-api.com/contenttiers/0cebb8be-46d7-c12a-d306-e9907bfc5a25/displayicon.png",
    "ExclusiveTier": "https://media.valorant-api.com/contenttiers/e046854e-406c-37f4-6607-19a9ba8426fc/displayicon.png",
    "PremiumTier": "https://media.valorant-api.com/contenttiers/60bca009-4182-7998-dee7-b8a2558dc369/displayicon.png",
    "SelectTier": "https://media.valorant-api.com/contenttiers/12683d76-48d7-84a3-4e09-6985794f0445/displayicon.png",
    "UltraTier": "https://media.valorant-api.com/contenttiers/411e4a55-4e59-7757-41f0-86a53f101bb5/displayicon.png",
    "ValorantPointIcon": "https://media.valorant-api.com/currencies/85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/largeicon.png",
    "RadianitePointIcon": "https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png",
}

tiers = {
    "0cebb8be-46d7-c12a-d306-e9907bfc5a25": {
        "name": "DeluxeTier",
        "emoji": "<:Deluxe:950372823048814632>",
        "color": 0x009587,
    },
    "e046854e-406c-37f4-6607-19a9ba8426fc": {
        "name": "ExclusiveTier",
        "emoji": "<:Exclusive:950372911036915762>",
        "color": 0xF1B82D,
    },
    "60bca009-4182-7998-dee7-b8a2558dc369": {
        "name": "PremiumTier",
        "emoji": "<:Premium:950376774620049489>",
        "color": 0xD1548D,
    },
    "12683d76-48d7-84a3-4e09-6985794f0445": {
        "name": "SelectTier",
        "emoji": "<:Select:950376833982021662>",
        "color": 0x5A9FE2,
    },
    "411e4a55-4e59-7757-41f0-86a53f101bb5": {
        "name": "UltraTier",
        "emoji": "<:Ultra:950376896745586719>",
        "color": 0xEFEB65,
    },
}

points = {
    "ValorantPointIcon": "<:ValorantPoint:950365917613817856>",
    "RadianitePointIcon": "<:RadianitePoint:950365909636235324>",
}

error_constructor = Translator()

def get_item_type(uuid: str) -> Optional[str]:
    """Get item type"""
    item_type = {
        "01bb38e1-da47-4e6a-9b3d-945fe4655707": "Agents",
        "f85cb6f7-33e5-4dc8-b609-ec7212301948": "Contracts",
        "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475": "Sprays",
        "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "Gun Buddies",
        "3f296c07-64c3-494c-923b-fe692a4fa1bd": "Player Cards",
        "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "Skins",
        "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "Skins chroma",
        "de7caa6b-adf7-4588-bbd1-143831e786c6": "Player titles",
    }
    return item_type.get(uuid)


async def url_to_image(url) -> Optional[bytes]:
    """从指定的URL获取图片并返回其字节。
    Args:
    url: 要获取图片的URL。

    Returns:
    获取到的图片的字节，如果发生错误则返回None。
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status in range(200, 299):
                return await response.read()


async def get_request_json(
        url: str,
        headers: Dict = None,
        proxy: object = plugin_config.valorant_proxies,
        sub_url: Optional[str] = "",
) -> Dict:
    """使用 aiohttp 从指定 URL 获取 JSON 数据。

    Args:
        sub_url: 要获取数据的 URL。
        url: 要获取数据的 URL。
        headers: 请求的头部信息。
        proxy: 可选参数，代理配置项。

    Returns:
        如果成功获取到 JSON 数据，则返回一个 Python 字典类型的数据，否则返回 None。
    """
    url = f"{url}{sub_url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
    except aiohttp.ClientError as e:
        raise ResponseError("API.REQUEST_FAILED") from e


async def put_request_json(
        url: str,
        data: [dict, list] = None,
        headers: Dict = None,
        proxy: object = plugin_config.valorant_proxies,
) -> Dict:
    """使用 aiohttp 发送 PUT 请求并获取 JSON 数据。

    Args:
        url: 要发送请求的 URL。
        data: 发送到 API 的数据。
        headers: 请求的头部信息。
        proxy: 可选参数，代理配置项。

    Returns:
        返回 API 的响应结果，如果成功获取到 JSON 数据，则返回一个 Python 字典类型的数据。

    Raises:
        ResponseError: 如果 API 返回的响应结果为空，则抛出异常。
    """
    data = data if data is not None else {}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                    url, headers=headers, json=data, proxy=proxy
            ) as response:
                response = await response.json()
                if response is not None:
                    return response
                else:
                    raise ResponseError("errors.API.REQUEST_FAILED")
    except aiohttp.ClientError:
        raise ResponseError("errors.API.REQUEST_FAILED")


def parse_skin(skin: Dict[str, Any]) -> Dict[str, Any]:
    """解析武器皮肤数据

    Args:
        skin: 武器皮肤数据

    Returns:
        解析后的武器皮肤数据
    """
    skin_uuid = skin["levels"][0]["uuid"]
    skin_names = skin["displayName"]
    skin_icon = skin["levels"][0]["displayIcon"]
    skin_tier = skin["contentTierUuid"]

    return {
        "uuid": json.dumps(skin_uuid),
        "names": skin_names,
        "icon": skin_icon,
        "tier": skin_tier if skin_tier is not None else "None",
        "hash": calculate_hash(f"{skin_uuid}{skin_names}{skin_icon}{skin_tier}")
    }


async def get_skin() -> Optional[Dict[str, Any]]:
    """获取武器皮肤数据

    Returns:
        武器皮肤数据
    """
    try:
        resp = await get_request_json(
            url=base_url, sub_url="weapons/skins?language=all"
        )
        if resp:
            skin = resp.get("data", [])
            return {
                parse_skin(skin)["uuid"]: parse_skin(skin)
                for skin in skin
            }
    except Exception as e:
        print(f"获取武器皮肤信息时发生错误：{e}")
    return None


def parse_tier(tier: Dict[str, Any]) -> Dict[str, Any]:
    """解析皮肤等级数据

    Args:
        tier: 皮肤等级数据

    Returns:
        解析后的皮肤等级数据
    """
    tier_uuid = tier["uuid"]
    tier_name = tier["devName"]
    tier_icon = tier["displayIcon"]

    return {
        "uuid": tier_uuid,
        "name": tier_name,
        "icon": tier_icon,
    }


async def get_tier() -> Optional[Dict[str, Any]]:
    """获取皮肤等级数据

    Returns:
        皮肤等级数据
    """
    try:
        resp = await get_request_json(url=base_url, sub_url="contenttiers/")
        if resp:
            tier = resp.get("data", [])
            return {
                parse_tier(tier)["uuid"]: parse_tier(tier)
                for tier in tier
            }
    except Exception as e:
        print(f"获取皮肤等级信息时发生错误：{e}")
    return None


async def parse_mission(mission: Dict[str, Any]) -> Dict[str, Any]:
    """解析任务数据

    Args:
        mission: 任务数据

    Returns:
        解析后的任务数据
    """
    mission_uuid = mission["uuid"]
    mission_titles = mission["title"]
    mission_type = mission["type"]
    mission_progress = mission["progressToComplete"]
    mission_xp = mission["xpGrant"]

    return {
        "uuid": mission_uuid,
        "titles": mission_titles,
        "type": mission_type,
        "progress": mission_progress,
        "xp": mission_xp,
    }


async def get_mission() -> Optional[Dict]:
    """获取任务数据

    Returns:
        解析后的任务数据
    """
    try:
        resp = await get_request_json(
            url=base_url, sub_url="missions?language=all"
        )
        if resp:
            missions = {}
            for mission in resp["data"]:
                mission_info = await parse_mission(mission)
                missions[mission_info["uuid"]] = mission_info
            return missions
    except Exception as e:
        print(f"获取任务数据时发生错误：{e}")
    return None


def parse_playercard(card: Dict[str, Any]) -> Dict[str, Any]:
    """解析玩家旗帜数据

    Args:
        card: 玩家旗帜数据

    Returns:
        解析后的玩家旗帜数据
    """
    card_uuid = card["uuid"]
    card_names = card["displayName"]
    card_icon = {
        "small": card["smallArt"],
        "wide": card["wideArt"],
        "large": card["largeArt"],
    }

    return {
        "uuid": card_uuid,
        "names": card_names,
        "icon": card_icon,
    }


async def get_playercards() -> Optional[Dict]:
    """获取玩家旗帜数据

    Returns:
        玩家旗帜数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("playercards?language=all")
        if resp:
            return {card["uuid"]: parse_playercard(card) for card in resp["data"]}
    except Exception as e:
        print(f"获取玩家旗帜信息时发生错误：{e}")
    return None


def parse_title(player_title: Dict[str, Any]) -> Dict[str, Any]:
    """解析玩家称号数据

    Args:
        player_title: 玩家称号数据

    Returns:
        解析后的玩家称号数据
    """
    title_uuid = player_title["uuid"]
    title_names = player_title["displayName"]
    title_text = player_title["titleText"]

    return {
        "uuid": title_uuid,
        "names": title_names,
        "text": title_text,
    }


async def get_player_titles() -> Optional[Dict]:
    """使用 aiohttp 从 valorant-api.com 获取玩家称号数据。

    Returns:
        玩家称号数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("playertitles?language=all")
        if resp:
            return {title["uuid"]: parse_title(title) for title in resp["data"]}
    except Exception as e:
        print(f"获取玩家称号信息时发生错误：{e}")
    return None


def parse_spray(spray: Dict[str, Any]) -> Dict[str, Any]:
    """解析喷漆数据

    Args:
        spray: 喷漆数据

    Returns:
        解析后的喷漆数据
    """
    spray_uuid = spray["uuid"]
    spray_names = spray["displayName"]
    spray_icon = spray["fullTransparentIcon"] or spray["displayIcon"]

    return {
        "uuid": spray_uuid,
        "names": spray_names,
        "icon": spray_icon,
    }


async def get_spray() -> Optional[Dict]:
    """获取喷漆数据

    Returns:
        喷漆数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("sprays?language=all")
        if resp:
            return {spray["uuid"]: parse_spray(spray) for spray in resp["data"]}
    except Exception as e:
        print(f"获取喷漆信息时发生错误：{e}")
    return None


def parse_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """解析套装数据

    Args:
        bundle: 套装数据

    Returns:
        解析后的套装数据
    """
    default_item = {"amount": 1, "discount": 0}
    items = []

    for weapon in bundle.get("weapons", []):
        weapon_item = {
            "uuid": weapon["levels"][0]["uuid"],
            "type": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
            "price": weapon.get("price"),
            **default_item,
        }
        items.append(weapon_item)

    for buddy in bundle.get("buddies", []):
        buddy_item = {
            "uuid": buddy["levels"][0]["uuid"],
            "type": "dd3bf334-87f3-40bd-b043-682a57a8dc3a",
            "price": buddy.get("price"),
            **default_item,
        }
        items.append(buddy_item)

    for card in bundle.get("cards", []):
        card_item = {
            "uuid": card["uuid"],
            "type": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
            "price": card.get("price"),
            **default_item,
        }
        items.append(card_item)

    for spray in bundle.get("sprays", []):
        spray_item = {
            "uuid": spray["uuid"],
            "type": "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475",
            "price": spray.get("price"),
            **default_item,
        }
        items.append(spray_item)

    return {
        "uuid": bundle["uuid"],
        "names": bundle["displayName"],
        "subnames": bundle["displayNameSubText"],
        "descriptions": bundle["extraDescription"],
        "icon": bundle["displayIcon2"],
        "items": items,
        "price": bundle.get("price"),
        "basePrice": None,
        "expires": None,
    }


async def get_bundle() -> Optional[Dict]:
    """获取套装数据

    Returns:
        套装数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("bundles?language=all")
        if resp:
            bundles = {}
            for bundle in resp["data"]:
                bundle_info = parse_bundle(bundle)
                bundles[bundle_info["uuid"]] = bundle_info
            return bundles
    except Exception as e:
        print(f"获取套装信息时发生错误：{e}")
    return None


def parse_contract(contract: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """解析合同数据

    Args:
        contract: 合同数据

    Returns:
        解析后的合同数据
    """
    ignor_contract = [
        "7b06d4ce-e09a-48d5-8215-df9901376fa7",  # BP EP 1 ACT 1
        "ed0b331b-45f2-115c-c958-3c9683ff5b5e",  # BP EP 1 ACT 2
        "e5c5ee7c-ac93-4f3b-8b76-cc7a2c66bf24",  # BP EP 1 ACT 3
        "4cff28f8-47e9-62e5-2625-49a517f981d2",  # BP EP 2 ACT 1
        "d1dfd006-4efa-7ef2-a46f-3eb497fc26df",  # BP EP 2 ACT 2
        "5bef6de8-44d4-ac64-3df2-078e618fc0e3",  # BP EP 2 ACT 3
        "de37c775-4017-177a-8c64-a8bb414dae1f",  # BP EP 3 ACT 1
        "b0bd7062-4d62-1ff1-7920-b39622ee926b",  # BP EP 3 ACT 2
        "be540721-4d60-0675-a586-ecb14adcb5f7",  # BP EP 3 ACT 3
        "60f2e13a-4834-0a18-5f7b-02b1a97b7adb",  # BP EP 4 ACT 1
        # 'c1cd8895-4bd2-466d-e7ff-b489e3bc3775', # BP EP 4 ACT 2
    ]

    if contract["uuid"] in ignor_contract:
        return None

    return {
        "uuid": contract["uuid"],
        "free": contract["shipIt"],
        "names": contract["displayName"],
        "icon": contract["displayIcon"],
        "reward": contract["content"],
    }


async def get_contract() -> Optional[Dict]:
    """获取合同数据

    Returns:
        合同数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("contracts?language=all")
        if resp:
            contracts = {}
            for contract in resp["data"]:
                contract_info = parse_contract(contract)
                contracts[contract_info["uuid"]] = contract_info
            return contracts
    except Exception as e:
        print(f"获取合同信息时发生错误：{e}")
    return None


def parse_rank_tier(tier: Dict[str, Any]) -> Dict[str, Any]:
    """解析段位数据

    Args:
        tier: 段位数据

    Returns:
        解析后的段位数据
    """
    return {
        "tier": tier["tier"],
        "name": tier["tierName"],
        "subname": tier["divisionName"],
        "icon": tier["largeIcon"],
        "rankup": tier["rankTriangleUpIcon"],
        "rankdown": tier["rankTriangleDownIcon"],
    }


async def get_rank_tiers() -> Optional[Dict[str, Any]]:
    """获取段位数据

    Returns:
        段位数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("competitivetiers?language=all")
        if resp:
            data = {}
            for rank in data["data"]:
                for i in rank["tiers"]:
                    data[i["tier"]] = parse_rank_tier(i)
            return data
    except Exception as e:
        print(f"获取段位信息时发生错误：{e}")
    return None


def parse_currency(currency: Dict[str, Any]) -> Dict[str, Any]:
    """解析货币数据

    Args:
        currency: 货币数据

    Returns:
        解析后的货币数据
    """
    return {
        "uuid": currency["uuid"],
        "names": currency["displayName"],
        "icon": currency["displayIcon"],
    }


async def get_currencies() -> Optional[Dict]:
    """获取货币数据

    Returns:
        货币数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("currencies?language=all")
        if resp:
            return {
                currency["uuid"]: parse_currency(currency)
                for currency in resp["data"]
            }
    except Exception as e:
        print(f"获取货币信息时发生错误：{e}")
    return None


def parse_buddy(buddy: Dict[str, Any]) -> Dict[str, Any]:
    """解析buddy数据

    Args:
        buddy: buddy数据

    Returns:
        解析后的buddy数据
    """
    try:
        buddy_uuid = buddy["levels"][0]["uuid"]
        buddy_names = buddy["displayName"]
        buddy_icon = buddy["levels"][0]["displayIcon"]
    except DataParseError as error:
        DataParseError(f"解析buddy数据时发生错误：{error}")

    return {
        "uuid": buddy_uuid,
        "names": buddy_names,
        "icon": buddy_icon,
    }


async def get_buddies() -> Optional[Dict]:
    """获取所有buddy数据

    Returns:
        buddy数据，如果发生错误则返回None。
    """
    try:
        response = await get_request_json("buddies?language=all")
        if response:
            return {
                parse_buddy(buddy)["uuid"]: parse_buddy(buddy)
                for buddy in response["data"]
            }
    except ResponseError as error:
        ResponseError(f"buddy.request：{error}")
    except DataParseError as error:
        DataParseError(f"解析buddy数据时发生错误：{error}")
    except Exception as error:
        logger.error(f"发生未知异常：{error}")
    return None


def parse_skin_chroma(chroma: Dict[str, Any]) -> Dict[str, Any]:
    """解析武器外观染色数据

    Args:
        chroma: 武器外观染色数据

    Returns:
        解析后的武器外观染色数据
    """
    return {
        "uuid": chroma["uuid"],
        "names": chroma["displayName"],
        "icon": chroma["displayIcon"],
        "full_render": chroma["fullRender"],
        "swatch": chroma["swatch"],
        "video": chroma["streamedVideo"],
    }


async def get_skin_chromas() -> Optional[Dict[str, Dict[str, Any]]]:
    """获取所有皮肤染色数据

    Returns:
        所有皮肤染色数据，如果发生错误则返回 None。
    """
    try:
        resp = await get_request_json("weapons/skinchromas?language=all")
        if resp:
            chromas = {}
            for chroma in resp["data"]:
                chroma_info = parse_skin_chroma(chroma)
                chromas[chroma_info["uuid"]] = chroma_info
            return chromas
    except Exception as e:
        print(f"获取皮肤染色信息时发生错误：{e}")
    return None
