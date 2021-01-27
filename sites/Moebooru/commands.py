from telethon import events
from utils import NazurinError, handleBadRequest, sendDocuments, sendPhotos

from .api import Moebooru

moebooru = Moebooru()

@events.register(events.NewMessage(pattern=r'/yandere (\S+)'))
async def yandere_view(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id < 0:
            await event.reply('Invalid post id!')
            return
        imgs, details = moebooru.site('yande.re').view(post_id)
        await sendPhotos(event, imgs, details)
    except (IndexError, ValueError):
        await event.reply('Usage: /yandere <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(event, error)

@events.register(events.NewMessage(pattern=r'/yandere_download (\S+)'))
async def yandere_download(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id <= 0:
            await event.reply('Invalid post id!')
            return
        imgs = await moebooru.site('yande.re').download(post_id)
        await sendDocuments(event, imgs)
    except (IndexError, ValueError):
        await event.reply('Usage: /yandere_download <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)

@events.register(events.NewMessage(pattern=r'/konachan (\S+)'))
async def konachan_view(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id < 0:
            await event.reply('Invalid post id!')
            return
        imgs, details = moebooru.site('konachan.com').view(post_id)
        await sendPhotos(event, imgs, details)
    except (IndexError, ValueError):
        await event.reply('Usage: /konachan <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(event, error)

@events.register(events.NewMessage(pattern=r'/konachan_download (\S+)'))
async def konachan_download(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id <= 0:
            await event.reply('Invalid post id!')
            return
        imgs = await moebooru.site('konachan.com').download(post_id)
        await sendDocuments(event, imgs)
    except (IndexError, ValueError):
        await event.reply('Usage: /konachan_download <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)

commands = [
    yandere_view,
    yandere_download,
    konachan_view,
    konachan_download,
]
