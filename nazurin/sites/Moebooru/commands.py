from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot
from nazurin.utils import NazurinError, sendDocuments, sendPhotos

from .api import Moebooru

moebooru = Moebooru()

@bot.handler(filters.RegexpCommandsFilter(regexp_commands=[r'/yandere (\S+)']))
async def yandere_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        imgs, details = moebooru.site('yande.re').view(post_id)
        await sendPhotos(message, imgs, details)
    except (IndexError, ValueError):
        await message.reply('Usage: /yandere <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(message, error)

@bot.handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/yandere_download (\S+)']))
async def yandere_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        imgs = await moebooru.site('yande.re').download(post_id)
        await sendDocuments(message, imgs)
    except (IndexError, ValueError):
        await message.reply('Usage: /yandere_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

@bot.handler(filters.RegexpCommandsFilter(regexp_commands=[r'/konachan (\S+)'])
             )
async def konachan_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        imgs, details = moebooru.site('konachan.com').view(post_id)
        await sendPhotos(message, imgs, details)
    except (IndexError, ValueError):
        await message.reply('Usage: /konachan <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(message, error)

@bot.handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/konachan_download (\S+)'])
)
async def konachan_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        imgs = await moebooru.site('konachan.com').download(post_id)
        await sendDocuments(message, imgs)
    except (IndexError, ValueError):
        await message.reply('Usage: /konachan_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

commands = [
    yandere_view,
    yandere_download,
    konachan_view,
    konachan_download,
]
