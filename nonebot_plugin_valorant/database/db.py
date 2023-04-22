from sysconfig import get_path

from tortoise import Tortoise, run_async


class DB:

    @classmethod
    async def init(cls):
        config = {
            "connection":
                {
                    "valorant_bot": f"sqlite://{get_path('data.sqlite3')}"
                },
            "apps":
                {
                    "valorant_bot_app":
                        {
                            "models": ["valorant_bot.database.models"],
                            "default_connection": "valorant_bot",
                        }
                }
        }
        await Tortoise.init(config)

        await Tortoise.generate_schemas()

    run_async(init())
