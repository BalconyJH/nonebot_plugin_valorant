import nonebot
from nonebot import Bot
from nonebot.adapters.onebot.v11 import Adapter
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from typing import Union
from nonebot.exception import FinishedException


async def send_error_msg(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], error_message: str):
    if isinstance(event, PrivateMessageEvent):
        if event.sub_type == "group":
            raise FinishedException
        return
    await bot.send(event, error_message)


class NotOwner:
    """Raised when a command is used by a user who is not the owner of the bot."""

    pass


class BadArgument:
    """Raised when a command's argument could not be found."""

    pass


class ValorantBotError:
    """base class for all errors raised by the bot"""

    pass


# https://github.com/colinhartigan/valclient.py/blob/0dcff9e384943a2889e6b3f8e71781c9fc950bce/src/valclient/exceptions.py#L1


class ResponseError:
    """
    Raised whenever an empty response is given by the Riot server.
    """

    pass


class HandshakeError:
    """
    Raised whenever there's a problem while attempting to communicate with the local Riot server.
    """

    pass


class AuthenticationError(Exception):
    """
    Raised whenever there's a problem while attempting to authenticate with the Riot server.
    """

    pass


class DatabaseError:
    """
    Raised whenever there's a problem while attempting to access the database.
    """

    pass