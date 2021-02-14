from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import NazurinError

from .api import Danbooru

danbooru = Danbooru()

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/danbooru (\S+)']))
async def danbooru_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        illust = await danbooru.view(post_id)
        await bot.sendPhotos(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /danbooru <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/danbooru_download (\S+)'])
)
async def danbooru_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        illust = await danbooru.view(post_id)
        await illust.download()
        await bot.sendDocuments(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /danbooru_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)
