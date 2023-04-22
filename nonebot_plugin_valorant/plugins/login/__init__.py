from nonebot.adapters.onebot.v11.event import PrivateMessageEvent

from nonebot.adapters.onebot.v11.event import PrivateMessageEvent

from ...utils import (on_command)

login = on_command("login", priority=5, block=True)


@login.handle()
async def _(event: PrivateMessageEvent):
