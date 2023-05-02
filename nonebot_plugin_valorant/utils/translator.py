import json
from pathlib import Path

from nonebot_plugin_valorant.config import plugin_config
from nonebot.log import logger
from nonebot_plugin_valorant.utils.errors import FileExistError

translations_path = Path(__file__).parent.parent / "resources" / "translations" / f"{plugin_config.language_type}.json"


class Translator:
    def __init__(self):
        """
        加载指定语言的翻译文件并初始化翻译器。
        """
        try:
            with open(translations_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileExistsError as e:
            raise FileExistError("文件已损坏或丢失") from e  # TODO:使用翻译器内容替代

    @staticmethod
    def get_value_by_key(data, key):
        """
        获取指定键的值。
        """
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for k, v in item.items():
                    if k == key:
                        return v
                    stack.append(v)
            elif isinstance(item, list):
                stack.extend(iter(item))
            elif key in (item, item.split('.')[-1]):
                return item
        return None

    def gettext(self, message_key):
        """
        获取指定消息键的翻译文本。
        """
        return self.get_value_by_key(self.translations, message_key)

    def get_translation(self, *message_keys):
        """
        获取多个消息键的翻译文本。
        """
        return {key: self.gettext(key) for key in message_keys}

# def message_translator(message_key: str) -> str:
#     """
#     获取指定消息键的翻译文本。
#     """
#     return Translator().gettext(message_key)
