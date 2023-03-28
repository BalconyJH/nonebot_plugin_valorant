from typing import Optional

from nonebot import get_driver
from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    language_type: str = "zh_CN"
    database: Optional[str] = None


global_config = get_driver().config
plugin_config = Config.parse_obj(global_config)
