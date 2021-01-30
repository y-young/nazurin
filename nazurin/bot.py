from typing import List, Union

from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import AllowedUpdates, Message
from aiogram.utils.executor import start_webhook

from nazurin import config
from nazurin.utils import getUrlsFromMessage, logger

_HANDLER_ATTRS = '__nazurin.handler'

def handler(*args, **kwargs):
    def decorator(callback):
        setattr(callback, _HANDLER_ATTRS, (args, kwargs))
        return callback

    return decorator

class AuthMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        if config.IS_PUBLIC:
            return
        if message.chat.id in config.ALLOW_ID + config.ALLOW_GROUP\
            or message.from_user.id in config.ALLOW_ID\
            or message.from_user.username in config.ALLOW_USERNAME:
            return
        raise CancelHandler()

class URLFilter(BoundFilter):
    key = 'url'

    async def check(self, message: Message) -> Union[List[str], bool]:
        urls = getUrlsFromMessage(message)
        if urls:
            return {'urls': urls}
        return False

class Nazurin(Dispatcher):
    def __init__(self):
        bot = Bot(token=config.TOKEN)
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
        await self.bot.delete_webhook()

    def start(self):
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
