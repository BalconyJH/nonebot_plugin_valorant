from nonebot_plugin_valorant.utils.reqlib.request_res import get_request_json_data


async def get_client_version() -> str:
    """
    获取 Valorant 客户端版本信息。

    Returns:
        str: 客户端版本信息，格式为 "<分支>-shipping-<构建版本>-<第四位版本号>"。
    """
    data = await get_request_json_data("version")
    return f"{data['data']['branch']}-shipping-{data['data']['buildVersion']}-{data['data']['version'].split('.')[3]}"


async def get_valorant_version() -> str:
    """
    获取 VALORANT 版本号。

    Returns:
        str: VALORANT 版本号。
    """
    data = await get_request_json_data("version")
    return data["data"]["version"]


async def get_manifest_id():
    """
    获取最新的资源清单值。

    Returns:
        str: 资源清单值。
    """
    resp = await get_request_json_data("version")
    return resp["data"]["manifestId"]
