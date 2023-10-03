# 使用 md2pic
import io
from pathlib import Path
from typing import Union

from PIL import Image as Img
from nonebot import require, on_command
from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_saa import Image, MessageFactory
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PrivateMessageEventV11
from nonebot.adapters.onebot.v12 import PrivateMessageEvent as PrivateMessageEventV12

require("nonebot_plugin_htmlrender")
agreement = on_command("协议", aliases={"agreement"}, priority=5, block=True)

md = Path(__file__).parent / "agreement.md"


@agreement.handle()
async def _md2pic(event: Union[PrivateMessageEventV11, PrivateMessageEventV12]):
    with open(md, "r", encoding="utf-8") as file:
        agreement_content = file.read()

    pic = await md_to_pic(md=agreement_content)

    msg_builder = MessageFactory(Image(pic))
    await msg_builder.send()
    await agreement.finish()
