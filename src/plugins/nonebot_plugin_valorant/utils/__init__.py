import json
from pathlib import Path

from ..config import Config

translations_path = Path(__file__).parent.parent / "translations" / f"{Config.language_type}.json"


class Translator:
    def __init__(self):
        """
        加载指定语言的翻译文件并初始化翻译器。
        """
        with open(translations_path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

    def gettext(self, message_key):
        """
        获取指定消息键的翻译文本。
        """
        return self.translations.get(message_key, message_key)

    def get_translation(self, message_key):
        """
        获取指定消息键的翻译文本。
        """
        return self.gettext(message_key)
