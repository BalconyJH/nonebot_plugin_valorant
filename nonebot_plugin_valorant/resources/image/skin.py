import os
import asyncio

import aiohttp
import aiofiles
from tqdm import tqdm
from nonebot import logger

from nonebot_plugin_valorant.config import plugin_config


async def download_image(session, url, uuid, pbar):
    response = await session.get(url)
    if response.status == 200:
        image_extension = url.split(".")[-1]
        image_filename = f"{uuid}.{image_extension}"
        image_path = os.path.join(plugin_config.resource_path, image_filename)

        async with aiofiles.open(image_path, "wb") as image_file:
            await image_file.write(await response.read())

        pbar.update(1)
    else:
        logger.warning(f"Failed to download image for UUID: {uuid}")


async def download_images_from_db(db_results) -> None:
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(db_results)) as pbar:
            tasks = []
            for uuid, icon in db_results:
                task = download_image(session, icon, uuid, pbar)
                tasks.append(task)
            await asyncio.gather(*tasks)
