from typing import List

from humanize import naturalsize

from nazurin import bot
from nazurin.config import MAX_PARALLEL_UPLOAD, env
from nazurin.models import File
from nazurin.utils import logger
from nazurin.utils.helpers import run_in_pool

ALBUM_ID = env.int("ALBUM_ID")


class Telegram:
    async def store(self, files: List[File]):
        tasks = []
        for file in files:
            size = await file.size()
            if size > 50 * 1024 * 1024:
                # Telegram bot currently only supports files up to 50MB
                # https://core.telegram.org/bots/api#senddocument
                logger.warning(
                    "File {} exceeds size limit ({}) and won't be save to Telegram",
                    file.name,
                    naturalsize(size, binary=True),
                )
                continue
            tasks.append(bot.send_doc(file, chat_id=ALBUM_ID))
        await run_in_pool(tasks, MAX_PARALLEL_UPLOAD)
        return True
