from html import escape
from mimetypes import guess_type
from typing import List

from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import (AllowedUpdates, ChatActions, InputFile,
                           InputMediaPhoto, Message)
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.executor import start_webhook

from nazurin import config
from nazurin.utils import logger
from nazurin.utils.decorators import chat_action, retry_after
from nazurin.utils.filters import URLFilter
from nazurin.utils.helpers import handleBadRequest

_HANDLER_ATTRS = '__nazurin.handler'

def handler(*args, **kwargs):
    def decorator(callback):
        setattr(callback, _HANDLER_ATTRS, (args, kwargs))
        return callback

    return decorator

@chat_action(ChatActions.UPLOAD_PHOTO)
@retry_after
async def sendPhotos(message: Message, imgs: List['Image'], details=None):
    if details is None:
        details = dict()
    media = list()
    if len(imgs) > 10:
        # TODO
        imgs = imgs[:10]
        await message.reply('Notice: Too many pages, sending only 10 of them')

    caption = str()
    for key, value in details.items():
        caption += str(key) + ': ' + str(value) + '\n'
    if len(caption) > 1024:
        caption = caption[:1024]
        await message.reply('Notice: Caption too long, trimmed')
    caption = escape(caption, quote=False)

    for img in imgs:
        filetype = str(guess_type(img.url)[0])
        if filetype.startswith('image'):
            media.append(InputMediaPhoto(img.display_url))
        else:
            await message.reply('File is not image, try download option.')
            return
    media[0].caption = caption
    try:
        await message.reply_media_group(media)
    except BadRequest as error:
        await handleBadRequest(message, error)

@retry_after
async def sendDocument(message: Message, img: 'Image', chat_id, message_id):
    await message.bot.send_document(chat_id,
                                    InputFile(img.path),
                                    reply_to_message_id=message_id)

@chat_action(ChatActions.UPLOAD_DOCUMENT)
async def sendDocuments(message: Message, imgs: List['Image'], chat_id=None):
    message_id = message.message_id
    if not chat_id:
        chat_id = message.chat.id
    else:
        message_id = None  # Sending to channel, no message to reply
    for img in imgs:
        await sendDocument(message, img, chat_id, message_id)

class AuthMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        if config.IS_PUBLIC:
            return
        if message.chat.id in config.ALLOW_ID + config.ALLOW_GROUP\
            or message.from_user.id in config.ALLOW_ID\
            or message.from_user.username in config.ALLOW_USERNAME:
            return
        raise CancelHandler()

class NazurinBot(Bot):
    send_message = retry_after(Bot.send_message)

class Nazurin(Dispatcher):
    def __init__(self):
        bot = NazurinBot(token=config.TOKEN)
        super().__init__(bot)
        self.middleware.setup(AuthMiddleware())
        self.filters_factory.bind(URLFilter,
                                  event_handlers=[self.message_handlers])

    def add_handler(self, callback):
        args, kwargs = getattr(callback, _HANDLER_ATTRS)
        self.register_message_handler(self.async_task(callback), *args,
                                      **kwargs)

    async def on_startup(self, dp):
        await self.bot.set_webhook(config.WEBHOOK_URL + config.TOKEN,
                                   allowed_updates=AllowedUpdates.MESSAGE)

    async def on_shutdown(self, dp):
        await self.bot.delete_webhook()  # TODO

    def start(self):
        # TODO
        if config.ENV == 'production':
            start_webhook(self,
                          webhook_path='/' + config.TOKEN,
                          on_startup=self.on_startup,
                          on_shutdown=self.on_shutdown,
                          skip_updates=True,
                          host="0.0.0.0",
                          port=config.PORT)
            logger.info('Set webhook')
        else:
            executor.start_polling(self, skip_updates=True)
