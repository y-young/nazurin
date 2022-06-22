import asyncio
from typing import List

from nazurin import bot
from nazurin.config import env
from nazurin.models import File

ALBUM_ID = env.int('ALBUM_ID')

class Telegram:
    async def store(self, files: List[File]):
        tasks = [bot.send_doc(file, chat_id=ALBUM_ID) for file in files]
        await asyncio.gather(*tasks)
        return True
