import random
from .api import Pixiv
from .config import IMG_PROXY
from utils import NazurinError, sendPhotos, sendDocuments, handleBadRequest
from telegram.ext import CommandHandler, Filters
from telegram.error import BadRequest

pixiv = Pixiv()

def pixiv_view(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(context.args[0])
        if artwork_id < 0:
            message.reply_text('Invalid artwork id!')
            return
        imgs, details = pixiv.view_illust(artwork_id)
        # use reverse proxy to avoid strange problems
        for img in imgs:
            img['url'] = img['url'].replace('i.pximg.net', IMG_PROXY)
            # img['url'] += '?' + str(random.random())
            img['thumbnail'] = img['thumbnail'].replace('i.pximg.net', IMG_PROXY)
            # img['thumbnail'] += '?' + str(random.random())
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv <artwork_id>')
    except NazurinError as error:
        message.reply_text(error.msg)
    except BadRequest as error:
        handleBadRequest(update, context, error)

def pixiv_download(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(context.args[0])
        if artwork_id < 0:
            message.reply_text('Invalid artwork id!')
            return
        imgs = pixiv.download_illust(artwork_id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv_download <artwork_id>')
    except NazurinError as error:
        message.reply_text(error.msg)

def pixiv_bookmark(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        artwork_id = int(context.args[0])
        if artwork_id < 0:
            message.reply_text('Invalid artwork id!')
            return
        context.dispatcher.run_async(pixiv.bookmark, artwork_id)
        message.reply_text('Done!')
    except (IndexError, ValueError):
        message.reply_text('Usage: /bookmark <artwork_id>')
    except NazurinError as error:
        message.reply_text(error.msg)

commands = [
    CommandHandler('pixiv', pixiv_view, pass_args=True, run_async=True),
    CommandHandler('pixiv_download', pixiv_download, pass_args=True, run_async=True),
    CommandHandler('bookmark', pixiv_bookmark, pass_args=True, run_async=True)
]