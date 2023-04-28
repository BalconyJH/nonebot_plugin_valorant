from typing import Optional, Union, List

from nonebot import get_driver
from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    valorant_language_type: str = "zh_CN"
    valorant_database: str = "mysql+pymysql://root:070499@localhost:3306/valorant_bot"
    valorant_proxies: str = "http://127.0.0.1:10809"
    valorant_timeout: int = 30
    valorant_to_me: bool = True
    valorant_command: Union[str, List[str]] = ""
    language_type: str = "zh_cn"


global_config = get_driver().config
plugin_config = Config.parse_obj(global_config)

