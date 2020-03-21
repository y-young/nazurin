from .api import Moebooru, MoebooruError
from utils import *
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async
from telegram.error import BadRequest

@run_async
def yandere_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('yandere')
        imgs, details = moebooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere <post_id>', quote=True)
    except BadRequest:
        handleBadRequest(update, context, error)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def yandere_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('yandere')
        imgs = moebooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere_download <post_id>', quote=True)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def konachan_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('konachan')
        imgs, details = moebooru.view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan <post_id>', quote=True)
    except BadRequest:
        handleBadRequest(update, context, error)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def konachan_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        moebooru = Moebooru('konachan')
        imgs = moebooru.download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan_download <post_id>', quote=True)
    except MoebooruError as error:
        message.reply_text(error.msg, quote=True)

commands = [
    CommandHandler('yandere', yandere_view, pass_args=True),
    CommandHandler('yandere_download', yandere_download, pass_args=True),
    CommandHandler('konachan', konachan_view, pass_args=True),
    CommandHandler('konachan_download', konachan_download, pass_args=True)
]