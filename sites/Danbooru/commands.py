from .api import Danbooru
from utils import NazurinError, sendPhotos, sendDocuments, handleBadRequest
from telegram.ext import CommandHandler
from telegram.error import BadRequest

danbooru = Danbooru()

def danbooru_view(update, context):
    message = update.message
    try:
        post_id = int(context.args[0])
        if post_id <= 0:
            message.reply_text('Invalid post id!')
            return
        imgs, details = danbooru.view(post_id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru <post_id>')
    except NazurinError as error:
        message.reply_text(error.msg)
    except BadRequest as error:
        handleBadRequest(update, context, error)

def danbooru_download(update, context):
    message = update.message
    try:
        post_id = int(context.args[0])
        if post_id <= 0:
            message.reply_text('Invalid post id!')
            return
        imgs = danbooru.download(post_id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /danbooru_download <post_id>')
    except NazurinError as error:
        message.reply_text(error.msg)

commands = [
    CommandHandler('danbooru', danbooru_view, pass_args=True, run_async=True),
    CommandHandler('danbooru_download', danbooru_download, pass_args=True, run_async=True)
]