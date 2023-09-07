import json
from pathlib import Path

from nonebot.log import logger

from nonebot_plugin_valorant.config import plugin_config

TRANSLATIONS_PATH = (
    Path(__file__).parent.parent
    / "resources"
    / "translations"
    / f"{plugin_config.language_type}.json"
)


class Translator:
    """
    消息翻译组件。
    """

    def __init__(self):
        """
        加载指定语言的翻译文件并初始化翻译器。
        """
        try:
            with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"找不到翻译文件: {e}")

    def extract_value(self, key_sequence):
        """
        从给定的JSON数据中，根据键序列抽取值
        :param self: 输入的JSON数据
        :param key_sequence: 键序列，例如"commands.login.NAME"
        :return: 如果找到，则返回对应的值，否则返回None
        """

        keys = key_sequence.split(".")
        data = self.translations

        for key in keys:
            if key in data:
                data = data[key]
            else:
                raise ValueError

        return data

    def get_local_translation(self, message_keys):
        """
        获取指定消息键的翻译文本。
        """
        return self.extract_value(message_keys)

    def get_local_translations(self, *message_keys):
        """
        获取多个消息键的翻译文本。
        """
        return {key: self.get_local_translation(key) for key in message_keys}
