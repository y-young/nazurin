from telethon import events
from utils import NazurinError, handleBadRequest, sendDocuments, sendPhotos

from .api import Pixiv

pixiv = Pixiv()

@events.register(events.NewMessage(pattern=r'/pixiv (\S+)'))
async def pixiv_view(event):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(event.pattern_match.group(1))
        if artwork_id < 0:
            await event.reply('Invalid artwork id!')
            return
        imgs, details = pixiv.view_illust(artwork_id)
        await sendPhotos(event, imgs, details)
    except (IndexError, ValueError):
        await event.reply('Usage: /pixiv <artwork_id>')
    except NazurinError as error:
        await event.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(update, context, error)

@events.register(events.NewMessage(pattern=r'/pixiv_download (\S+)'))
async def pixiv_download(event):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(event.pattern_match.group(1))
        if artwork_id < 0:
            await event.reply('Invalid artwork id!')
            return
        imgs = pixiv.download_illust(artwork_id)
        await sendDocuments(event, imgs)
    except (IndexError, ValueError):
        await event.reply('Usage: /pixiv_download <artwork_id>')
    except NazurinError as error:
        await event.reply(error.msg)

@events.register(events.NewMessage(pattern=r'/pixiv_bookmark (\S+)'))
async def pixiv_bookmark(event):
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(event.pattern_match.group(1))
        if artwork_id < 0:
            await event.reply('Invalid artwork id!')
            return
        pixiv.bookmark(artwork_id)
        await event.reply('Done!')
    except (IndexError, ValueError):
        await event.reply('Usage: /bookmark <artwork_id>')
    except NazurinError as error:
        await event.reply(error.msg)

commands = [pixiv_view, pixiv_download, pixiv_bookmark]
