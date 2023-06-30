from typing import Union, List

from nonebot import get_driver
from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    valorant_database: str = ""
    valorant_database_key_path: str = None
    valorant_proxies: str = ""
    valorant_timeout: int
    valorant_to_me: bool = True
    valorant_command: Union[str, List[str]] = ""
    language_type: str = ""


global_config = get_driver().config
plugin_config = Config.parse_obj(global_config)

