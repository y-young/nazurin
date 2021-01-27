from telethon import events
from utils import NazurinError, handleBadRequest, sendDocuments, sendPhotos

from .api import Danbooru

danbooru = Danbooru()

@events.register(events.NewMessage(pattern=r'/danbooru (\S+)'))
async def danbooru_view(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id <= 0:
            await event.reply('Invalid post id!')
            return
        imgs, details = danbooru.view(post_id)
        await sendPhotos(event, imgs, details)
    except (IndexError, ValueError):
        await event.reply('Usage: /danbooru <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)
    # except BadRequest as error:
    #     handleBadRequest(event, error)

@events.register(events.NewMessage(pattern=r'/danbooru_download (\S+)'))
async def danbooru_download(event):
    try:
        post_id = int(event.pattern_match.group(1))
        if post_id <= 0:
            await event.reply('Invalid post id!')
            return
        imgs = danbooru.download(post_id)
        await sendDocuments(event, imgs)
    except (IndexError, ValueError):
        await event.reply('Usage: /danbooru_download <post_id>')
    except NazurinError as error:
        await event.reply(error.msg)

commands = [danbooru_view, danbooru_download]
