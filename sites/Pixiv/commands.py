from .api import Pixiv, PixivError
from utils import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from telegram.error import BadRequest

pixiv = Pixiv()

@run_async
def pixiv_view(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        is_admin = message.from_user.id == ADMIN_ID
        imgs, details = pixiv.view(id, is_admin)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason, quote=True)
    except BadRequest as error:
        handleBadRequest(update, context, error)

@run_async
def pixiv_download(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        imgs = pixiv.download(id=id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /pixiv_download <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason, quote=True)

@run_async
def pixiv_bookmark(update, context):
    message = update.message
    try:
        # args[0] should contain the queried artwork id
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid artwork id!', quote=True)
            return
        pixiv.bookmark(id)
        message.reply_text('Done!', quote=True)
    except (IndexError, ValueError):
        message.reply_text('Usage: /bookmark <artwork_id>', quote=True)
    except PixivError as error:
        message.reply_text(error.reason)

commands = [
    CommandHandler('pixiv', pixiv_view, pass_args=True),
    CommandHandler('pixiv_download', pixiv_download, pass_args=True),
    CommandHandler('bookmark', pixiv_bookmark, Filters.user(user_id=ADMIN_ID), pass_args=True)
]