import aiohttp

from nonebot_plugin_valorant.config import plugin_config


async def get_client_version():
    """
    异步获取 Valorant 客户端版本信息

    Returns:
        str: 客户端版本信息，格式为 "<分支>-shipping-<构建版本>-<第四位版本号>"
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://valorant-api.com/v1/version", proxy=plugin_config.valorant_proxies) as response:
            if response.status == 200:
                data = await response.json()
                return f"{data['data']['branch']}-shipping-{data['data']['buildVersion']}-{data['data']['version'].split('.')[3]}"
    return None


async def get_valorant_version():
    """异步获取 VALORANT 版本号

    Returns:
        str: VALORANT 版本号，如果获取失败则返回 None
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://valorant-api.com/v1/version", proxy=plugin_config.valorant_proxies) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["version"]
    return None
