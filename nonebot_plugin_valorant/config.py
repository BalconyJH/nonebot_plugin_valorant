from pathlib import Path
from typing import List, Union

from nonebot import get_driver
from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    """
    This class represents the configuration settings for the application.

    Attributes:
        valorant_database (str): The path to the Valorant database.
        valorant_database_key_path (str): The path to the key file for Valorant database encryption.
        valorant_proxies (str): The list of proxy URLs for Valorant requests.
        valorant_timeout (int): The timeout duration for Valorant requests in seconds.
        valorant_to_me (bool): Whether to receive Valorant messages only addressed to the bot.
        valorant_command (Union[str, List[str]]): The command or list of commands to trigger Valorant actions.
        language_type (str): The type of language to use in the application's responses.
    """

    valorant_database: str = ""
    valorant_database_key_path: str = ""
    valorant_proxies: str = ""
    valorant_timeout: int
    valorant_to_me: bool = True
    valorant_command: Union[str, List[str]] = ""
    language_type: str = ""
    resource_path = Path(__file__).parent / "resources" / "image" / "skin"


global_config = get_driver().config
plugin_config = Config.parse_obj(global_config)
