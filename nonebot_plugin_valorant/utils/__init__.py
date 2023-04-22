import httpx
from nonebot import on_command as _on_command, require
from tortoise import Tortoise

from .. import config


def on_command(cmd, *args, **kwargs):
    return _on_command(config.valorant_command + cmd, *args, **kwargs)


def check_proxy():
    """检查代理是否有效"""
    if config.valorant_proxies:
        try:
            httpx.get(
                "https://icanhazip.com/",
                proxies={"all://": config.valorant_proxies},
                timeout=2,
            )
        except Exception as e:
            raise RuntimeError("代理无效，请检查代理") from e


async def check_db():
    """检查数据库是否有效"""
    try:
        await Tortoise.init(
            db_url=config.valorant_database,  # MySQL连接URL
            modules={'models': ['__main__']})
        conn = Tortoise.get_connection('default')
        await conn.execute_query('SELECT 1')
        print("数据库连接正常")
    except Exception as e:
        raise RuntimeError("数据库无效，请检查数据库") from e
    finally:
        await Tortoise.close_connections()


def on_startup():
    """启动前检查"""
    check_proxy()
    check_db()


PROXIES = {"all://": config.valorant_proxies}

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # noqa
