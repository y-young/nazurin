from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot
from nazurin.utils.exceptions import NazurinError

from .api import Pixiv

pixiv = Pixiv()

@bot.handler(filters.RegexpCommandsFilter(regexp_commands=[r'/pixiv (\S+)']))
async def pixiv_view(message: Message, regexp_command):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(regexp_command.group(1))
        if artwork_id < 0:
            await message.reply('Invalid artwork id!')
            return
        imgs, caption = await pixiv.view_illust(artwork_id)
        await bot.sendPhotos(message, imgs, caption)
    except (IndexError, ValueError):
        await message.reply('Usage: /pixiv <artwork_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@bot.handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/pixiv_download (\S+)']))
async def pixiv_download(message: Message, regexp_command):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(regexp_command.group(1))
        if artwork_id < 0:
            await message.reply('Invalid artwork id!')
            return
        imgs = await pixiv.download_illust(artwork_id)
        await bot.sendDocuments(message, imgs)
    except (IndexError, ValueError):
        await message.reply('Usage: /pixiv_download <artwork_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@bot.handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/pixiv_bookmark (\S+)']))
async def pixiv_bookmark(message: Message, regexp_command):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(regexp_command.group(1))
        if artwork_id < 0:
            await message.reply('Invalid artwork id!')
            return
        await pixiv.bookmark(artwork_id)
        await message.reply('Done!')
    except (IndexError, ValueError):
        await message.reply('Usage: /bookmark <artwork_id>')
    except NazurinError as error:
        await message.reply(error.msg)

commands = [pixiv_view, pixiv_download, pixiv_bookmark]
