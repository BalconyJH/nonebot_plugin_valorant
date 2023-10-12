import nonebot
from nonebot.adapters.onebot.v11 import Adapter as AdapterV11
from nonebot.adapters.onebot.v12 import Adapter as AdapterV12

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(AdapterV11)
driver.register_adapter(AdapterV12)

# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_plugin("nonebot_plugin_sentry")
nonebot.load_plugin("nonebot_plugin_htmlrender")
nonebot.load_plugins("nonebot_plugin_valorant/plugins")  # 本地插件

if __name__ == "__main__":
    nonebot.run()
