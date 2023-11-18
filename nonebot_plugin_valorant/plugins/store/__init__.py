from nonebot import on_command
from nonebot.params import T_State
from nonebot_plugin_saa import Image, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

from nonebot_plugin_valorant.database.db import DB
from nonebot_plugin_valorant.utils.requestlib.auth import Auth
from nonebot_plugin_valorant.utils.parsinglib.endpoint_parsing import SkinsPanel
from nonebot_plugin_valorant.utils import AuthenticationError, message_translator
from nonebot_plugin_valorant.utils.requestlib.player_info import PlayerInformation
from nonebot_plugin_valorant.utils.render.storefront_skinpanel import parse_user_info, render_skin_panel

store = on_command("store", aliases={"商店"}, priority=5, block=True)
test = on_command("test", aliases={"test"}, priority=5, block=True)
auth = Auth()


store.handle()
store.__doc__ = """商店"""


async def cache_skins_store_into_db(user_data: PlayerInformation, skin_data: SkinsPanel) -> None:
    """缓存商店皮肤信息到数据库"""
    await DB.cache_player_skins_store(
        puuid=user_data.puuid,
        offer_1=skin_data.skin1.uuid,
        offer_2=skin_data.skin2.uuid,
        offer_3=skin_data.skin3.uuid,
        offer_4=skin_data.skin4.uuid,
        duration=skin_data.duration,
    )


async def invalid_login_credentials(
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    state: T_State,
):
    await DB.logout(event.get_user_id())
    # await DB.delete_player_skins_store(event.get_user_id())


@store.handle()
async def _(
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    state: T_State,
):
    # tracer = VizTracer()
    # tracer.start()
    try:
        skin_data, player_info = await parse_user_info(event.get_user_id())
        await cache_skins_store_into_db(player_info, skin_data)
        pic = await render_skin_panel(skin_data)
        msg_builder = MessageFactory(Image(pic))
        await msg_builder.send()
        await store.finish()
    except AuthenticationError as e:
        await invalid_login_credentials(event, state)
        await store.finish(message_translator(f"{e}"))
    # tracer.stop()
    # tracer.save("test.html")


@test.handle()
async def _test(
    event: PrivateMessageEventV11 | PrivateMessageEventV12,
    state: T_State,
):
    pass
