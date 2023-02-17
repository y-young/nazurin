import asyncio
from typing import List

from aiogram import Dispatcher, executor
from aiogram.types import AllowedUpdates, ContentType, Message
from aiogram.utils.executor import Executor

from nazurin import config
from nazurin.utils import logger
from nazurin.utils.filters import URLFilter

from .bot import NazurinBot
from .middleware import AuthMiddleware
from .server import NazurinServer

class NazurinDispatcher(Dispatcher):
    def __init__(self, bot: NazurinBot):
        super().__init__(bot)
        self.middleware.setup(AuthMiddleware())
        self.filters_factory.bind(URLFilter,
                                  event_handlers=[self.message_handlers])
        self.server = NazurinServer(bot)
        self.server.on_startup.append(self.on_startup)
        self.executor = Executor(self)

    def init(self):
        self.bot.init()
        self.register_message_handler(
            self.update_collection,
            URLFilter(),
            content_types=[ContentType.TEXT, ContentType.PHOTO])

    def register_message_handler(self, callback, *args, **kwargs):
        return super().register_message_handler(self.async_task(callback),
                                                *args, **kwargs)

    async def on_startup(self, *_args):
        await self.bot.set_webhook(config.WEBHOOK_URL + config.TOKEN,
                                   allowed_updates=AllowedUpdates.MESSAGE)

    def start(self):
        self.init()
        if config.ENV == 'production':
            logger.info('Set webhook')
            self.executor.set_webhook(webhook_path='/' + config.TOKEN,
                                      web_app=self.server)
            # Tell aiohttp to use main thread event loop instead of creating a new one
            # otherwise bot commands will run in a different loop
            # from main thread functions and classes like Mongo and Mega.api_upload,
            # resulting in RuntimeError: Task attached to different loop
            self.executor.run_app(host=config.HOST,
                                  port=config.PORT,
                                  loop=asyncio.get_event_loop())
        else:
            # self.server.start()
            executor.start_polling(self, skip_updates=True)

    async def update_collection(self, message: Message, urls: List[str]):
        await self.bot.update_collection(urls, message)
        await message.reply('Done!')
