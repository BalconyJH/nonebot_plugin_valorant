import os
import asyncio

import aiohttp
import aiofiles
from tqdm import tqdm

from nonebot_plugin_valorant.database import DB
from nonebot_plugin_valorant.config import plugin_config


async def download_image(session, url, uuid, pbar):
    response = await session.get(url)
    if response.status == 200:
        image_extension = url.split(".")[-1]
        image_filename = f"{uuid}.{image_extension}"
        image_path = os.path.join(plugin_config.resource_path, image_filename)

        async with aiofiles.open(image_path, "wb") as image_file:
            await image_file.write(await response.read())

        pbar.update(1)  # 更新进度条
    else:
        print(f"Failed to download image for UUID: {uuid}")


async def download_images_from_db():
    results = await DB.get_all_skins_icon()
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(results)) as pbar:  # 创建进度条
            tasks = []
            for uuid, icon in results:
                task = download_image(session, icon, uuid, pbar)  # 将进度条对象传递给下载函数
                tasks.append(task)
            await asyncio.gather(*tasks)
