from aiogram.dispatcher import filters
from aiogram.types import Message

from nazurin import bot
from nazurin.utils import NazurinError, sendDocuments, sendPhotos

from .api import Zerochan

api = Zerochan()

@bot.handler(filters.RegexpCommandsFilter(regexp_commands=[r'/zerochan (\S+)'])
             )
async def zerochan_view(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id < 0:
            await message.reply('Invalid post id!')
            return
        imgs, details = api.view(post_id)
        await sendPhotos(message, imgs, details)
    except (IndexError, ValueError):
        await message.reply('Usage: /zerochan <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(message, error)

@bot.handler(
    filters.RegexpCommandsFilter(regexp_commands=[r'/zerochan_download (\S+)'])
)
async def zerochan_download(message: Message, regexp_command):
    try:
        post_id = int(regexp_command.group(1))
        if post_id <= 0:
            await message.reply('Invalid post id!')
            return
        imgs = await api.download(post_id)
        await sendDocuments(message, imgs)
    except (IndexError, ValueError):
        await message.reply('Usage: /zerochan_download <post_id>')
    except NazurinError as error:
        await message.reply(error.msg)

commands = [
    zerochan_view,
    zerochan_download,
]
