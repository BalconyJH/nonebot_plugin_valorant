from nonebot import Bot


class NotOwner(Bot.sent):
    """当非机器人所有者使用命令时，引发此异常。"""

    pass


class BadArgument(Bot.sent):
    """当无法找到命令的参数时引发此异常。"""

    pass


class BotError(Bot.sent):
    """所有由机器人引发的异常的基类。"""

    pass


class ResponseError(Bot.sent):
    """每当Riot服务器返回空响应时引发此异常。"""

    pass


class HandshakeError(Bot.sent):
    """每当尝试与本地Riot服务器通信时遇到问题时引发此异常。"""

    pass


class AuthenticationError(Bot.sent):
    """每当尝试与Riot服务器进行身份验证时遇到问题时引发此异常。"""

    pass


class DatabaseError(Bot.sent):
    """每当尝试访问数据库时遇到问题时引发此异常。"""

    # def __init__(self, message: str):
    #     super().__init__(message)
    #     logger.error(message)
    pass


class UnSupportedLogin(Bot.sent):
    """每当尝试使用不受支持的登录方式时引发此异常。"""

    pass
