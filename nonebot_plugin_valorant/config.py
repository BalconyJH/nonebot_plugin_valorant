from typing import Optional, Union, List

from nonebot import get_driver
from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    valorant_language_type: str = "zh_CN"
    valorant_database: str
    valorant_proxies: Optional[str] = None
    valorant_timeout: int = 30
    valorant_to_me: bool = True
    valorant_command: Union[str, List[str]] = ""


global_config = get_driver().config
plugin_config = Config.parse_obj(global_config)

