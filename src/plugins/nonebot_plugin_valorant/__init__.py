from plugins.nonebot_plugin_valorant.config import plugin_config

valorant_bot = ValorantBot(
    database=plugin_config.valorant_database,
    proxies=plugin_config.valorant_proxies,
    timeout=plugin_config.valorant_timeout,
    language=plugin_config.valorant_language_type,
)

matcher = create_matcher(

)

