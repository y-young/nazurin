from telethon import events
from utils import NazurinError, handleBadRequest, sendDocuments, sendPhotos

from .api import Zerochan

api = Zerochan()

@events.register(events.NewMessage(pattern=r'/zerochan (\S+)'))
async def zerochan_view(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id < 0:
            await event.reply('Invalid post id!')
            return
        imgs, details = api.view(post_id)
        await sendPhotos(event, imgs, details)
    except (IndexError, ValueError):
        await event.reply('Usage: /zerochan <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(event, error)

@events.register(events.NewMessage(pattern=r'/zerochan_download (\S+)'))
async def zerochan_download(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id <= 0:
            await event.reply('Invalid post id!')
            return
        imgs = api.download(post_id)
        await sendDocuments(event, imgs)
    except (IndexError, ValueError):
        await event.reply('Usage: /zerochan_download <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)

commands = [
    zerochan_view,
    zerochan_download,
]
