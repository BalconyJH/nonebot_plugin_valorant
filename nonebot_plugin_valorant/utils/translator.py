import json
from pathlib import Path

from nonebot_plugin_valorant.config import plugin_config

translations_path = Path(__file__).parent.parent / "resources" / "translations" / f"{plugin_config.language_type}.json"


class Translator:
    def __init__(self):
        """
        加载指定语言的翻译文件并初始化翻译器。
        """
        with open(translations_path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def get_value_by_key(self, data, key):
        """
        获取指定键的值。
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    return v
                elif isinstance(v, (dict, list)):
                    result = self.get_value_by_key(v, key)
                    if result is not None:
                        return result
        elif isinstance(data, list):
            values = [self.get_value_by_key(item, key) for item in data]
            return next((v for v in values if v is not None), None)
        elif key in (data, data.split('.')[-1]):
            return data
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

