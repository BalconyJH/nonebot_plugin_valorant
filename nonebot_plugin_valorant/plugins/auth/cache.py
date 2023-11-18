from nonebot import on_command

# from nonebot_plugin_valorant.utils.reqlib.auth import Auth

refresh = on_command("refresh", aliases={"刷新"}, priority=5, block=True)


async def cache_user():
    """当第一次登录的时候缓存钱包和皮肤库存"""
