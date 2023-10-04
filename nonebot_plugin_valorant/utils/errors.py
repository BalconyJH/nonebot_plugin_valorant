class TranslatableError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self) -> str:
        return self.__repr__()


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


class DataParseError(TranslatableError):
    """
    当无法解析数据时引发的异常。
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


class RequestError(TranslatableError):
    """
    请求 Riot 服务器时出现参数错误时引发的异常。
    """

    pass


class ConfigurationError(TranslatableError):
    """
    当配置文件中的值无效时引发的异常。
    """

    pass
