import asyncio

from nazurin import bot
from nazurin.config import env

ALBUM_ID = env.int('ALBUM_ID')

class Telegram(object):
    async def store(self, files):
        tasks = [bot.sendDocument(file, chat_id=ALBUM_ID) for file in files]
        await asyncio.gather(*tasks)
        return True
