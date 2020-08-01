from .api import Danbooru
from utils import *
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram.error import BadRequest

danbooru = Danbooru()

@run_async
def danbooru_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs, details = danbooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru <post_id>', quote=True)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)
    except BadRequest as error:
        handleBadRequest(update, context, error)

@run_async
def danbooru_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs = danbooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru_download <post_id>', quote=True)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)

commands = [
    CommandHandler('danbooru', danbooru_view, pass_args=True),
    CommandHandler('danbooru_download', danbooru_download, pass_args=True)
]