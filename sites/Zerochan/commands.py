from .api import Zerochan
from utils import sendPhotos, sendDocuments, handleBadRequest, NazurinError
from telegram.ext import CommandHandler, run_async
from telegram.error import BadRequest

api = Zerochan()

@run_async
def zerochan_view(update, context):
    message = update.message
    try:
        post_id = int(context.args[0])
        if post_id < 0:
            message.reply_text('Invalid post id!')
            return
        imgs, details = api.view(post_id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /zerochan <post_id>')
    except BadRequest as error:
        handleBadRequest(update, context, error)
    except NazurinError as error:
        message.reply_text(error.msg)

@run_async
def zerochan_download(update, context):
    message = update.message
    try:
        post_id = int(context.args[0])
        if post_id <= 0:
            message.reply_text('Invalid post id!')
            return
        imgs = api.download(post_id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /zerochan_download <post_id>')
    except NazurinError as error:
        message.reply_text(error.msg)

commands = [
    CommandHandler('zerochan', zerochan_view, pass_args=True),
    CommandHandler('zerochan_download', zerochan_download, pass_args=True)
]