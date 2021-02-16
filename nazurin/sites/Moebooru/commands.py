from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot, dp
from nazurin.utils.exceptions import NazurinError

from .api import Moebooru

moebooru = Moebooru()

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/yandere (\S+)']))
async def yandere_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        illust = await moebooru.site('yande.re').view(post_id)
        await bot.sendIllust(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /yandere <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/yandere_download (\S+)']))
async def yandere_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        illust = await moebooru.site('yande.re').view(post_id)
        await illust.download()
        await bot.sendDocuments(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /yandere_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/konachan (\S+)']))
async def konachan_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        illust = await moebooru.site('konachan.com').view(post_id)
        await bot.sendIllust(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /konachan <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/konachan_download (\S+)'])
)
async def konachan_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        illust = await moebooru.site('konachan.com').view(post_id)
        await illust.download()
        await bot.sendDocuments(illust, message)
    except (IndexError, ValueError):
        await message.reply('Usage: /konachan_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)
