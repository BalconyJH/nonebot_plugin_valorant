from typing import Union

from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import FinishedException


async def send_error_msg(
        bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], error_message: str
):
    """
    发送错误消息的异步函数。

    Args:
        bot (Bot): 机器人对象。
        event (Union[GroupMessageEvent, PrivateMessageEvent]): 事件对象。
        error_message (str): 错误消息。

    Returns:
        None
    """
    if isinstance(event, PrivateMessageEvent):
        if event.sub_type == "group":
            raise FinishedException
        return
    await bot.send(event, error_message)


class TranslatableError(Exception):
    def __init__(self, message):
        self.message = message

    # def __str__(self):
    #     return message_translator(self.message)


class NotOwner(TranslatableError):
    """
    当非机器人所有者使用命令时引发的异常。
    """

    pass


class NoneReturnError(TranslatableError):
    """
    当请求资源返回空时引发的异常。
    """

    pass


class BadArgument(TranslatableError):
    """
    当找不到命令的参数时引发的异常。
    """

    pass


class ValorantBotError(TranslatableError):
    """
    机器人引发的所有错误的基类。
    """

    pass


class ResponseError(TranslatableError):
    """
    当 Riot 服务器返回空响应时引发的异常。
    """

    pass


class HandshakeError(TranslatableError):
    """
    尝试与本地 Riot 服务器通信时出现问题时引发的异常。
    """

    pass


class AuthenticationError(TranslatableError):
    """
    尝试与 Riot 服务器进行身份验证时出现问题时引发的异常。
    """

    pass


class DatabaseError(TranslatableError):
    """
    尝试访问数据库时出现问题时引发的异常。
    """

    pass


class FileExistError(TranslatableError):
    pass
