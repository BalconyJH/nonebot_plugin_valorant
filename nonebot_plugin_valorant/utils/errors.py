from typing import Union

from nonebot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import FinishedException


async def send_error_msg(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], error_message: str):
    """
    发送错误消息的异步函数。

    Args:
        bot (Bot): 机器人对象。
        event (Union[GroupMessageEvent, PrivateMessageEvent]): 事件对象，可能是 GroupMessageEvent 或 PrivateMessageEvent。
        error_message (str): 错误消息。

    Returns:
        None
    """
    if isinstance(event, PrivateMessageEvent):
        if event.sub_type == "group":
            raise FinishedException
        return
    await bot.send(event, error_message)


class NotOwner:
    """
    当非机器人所有者使用命令时引发的异常。
    """

    pass


class BadArgument:
    """
    当找不到命令的参数时引发的异常。
    """

    pass


class ValorantBotError:
    """
    机器人引发的所有错误的基类。
    """

    pass


class ResponseError:
    """
    当 Riot 服务器返回空响应时引发的异常。
    """

    pass


class HandshakeError:
    """
    尝试与本地 Riot 服务器通信时出现问题时引发的异常。
    """

    pass


class AuthenticationError(Exception):
    """
    尝试与 Riot 服务器进行身份验证时出现问题时引发的异常。
    """

    pass


class DatabaseError:
    """
    尝试访问数据库时出现问题时引发的异常。
    """

    pass
