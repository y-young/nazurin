from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot, dp

from .api import Zerochan

api = Zerochan()

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/zerochan (\S+)']))
async def zerochan_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        illust = await api.view(post_id)
        await bot.sendIllust(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /zerochan <post_id>')

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/zerochan_download (\S+)'])
)
async def zerochan_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        illust = await api.view(post_id)
        await illust.download()
        await bot.sendDocuments(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /zerochan_download <post_id>')
