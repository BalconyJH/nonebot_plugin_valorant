from nonebot import  on_command

test = on_command("test")

@test.handle()
async def test_handle(bot, event):
    await test.finish("test")