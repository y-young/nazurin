from .api import Moebooru
from utils import *
from telegram.ext import CommandHandler, run_async
from telegram.error import BadRequest

moebooru = Moebooru()

@run_async
def yandere_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs, details = moebooru.site('yande.re').view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere <post_id>', quote=True)
    except BadRequest as error:
        handleBadRequest(update, context, error)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def yandere_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs = moebooru.site('yande.re').download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /yandere_download <post_id>', quote=True)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def konachan_view(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id < 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs, details = moebooru.site('konachan.com').view(id)
        sendPhotos(update, context, imgs, details)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan <post_id>', quote=True)
    except BadRequest as error:
        handleBadRequest(update, context, error)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)

@run_async
def konachan_download(update, context):
    message = update.message
    try:
        id = int(context.args[0])
        if id <= 0:
            message.reply_text('Invalid post id!', quote=True)
            return
        imgs = moebooru.site('konachan.com').download(id)
        sendDocuments(update, context, imgs)
    except (IndexError, ValueError):
        message.reply_text('Usage: /konachan_download <post_id>', quote=True)
    except NazurinError as error:
        message.reply_text(error.msg, quote=True)

commands = [
    CommandHandler('yandere', yandere_view, pass_args=True),
    CommandHandler('yandere_download', yandere_download, pass_args=True),
    CommandHandler('konachan', konachan_view, pass_args=True),
    CommandHandler('konachan_download', konachan_download, pass_args=True)
]