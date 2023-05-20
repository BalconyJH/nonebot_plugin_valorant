from importlib.metadata import version

from nonebot_plugin_valorant.utils.reqlib.request_res import get_request_json_data, base_url


# async def get_client_version() -> str:
#     """
#     获取 Valorant 客户端版本信息。
#
#     Returns:
#         str: 客户端版本信息，格式为 "<分支>-shipping-<构建版本>-<第四位版本号>"。
#     """
#     data = await get_request_json_data(url=base_url, sub_url="version")
#     return f"{data['data']['branch']}-shipping-{data['data']['buildVersion']}-{data['data']['version'].split('.')[3]}"

async def get_version_data() -> dict:
    data = await get_request_json_data(url=base_url, sub_url="version")
    version_data = data.get("data", {})
    version_data.pop("status", None)
    return version_data


async def get_valorant_version() -> str:
    """
    获取 VALORANT 版本号。

    Returns:
        str: VALORANT 版本号。
    """
    data = await get_request_json_data(url=base_url, sub_url="version")
    return data["data"]["version"]


async def get_manifest_id() -> str:
    """
    获取最新的资源清单值。

    Returns:
        str: 资源清单值。
    """
    data = await get_request_json_data(url=base_url, sub_url="version")
    return data["data"]["manifestId"]


async def get_bot_version() -> str:
    return version('nonebot_plugin_valorant')


async def get_version() -> dict:
    data = await get_request_json_data(url=base_url, sub_url="version")
    print(data["data"]["manifestId"])
    return {
        version: method() if callable(method) else method
        for version, method in data.items()
    }
