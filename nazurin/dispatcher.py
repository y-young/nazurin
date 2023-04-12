import asyncio
from typing import List

from aiogram import Dispatcher
from aiogram.types import AllowedUpdates, ContentType, Message, Update
from aiogram.utils.executor import Executor

from nazurin import config
from nazurin.utils import logger
from nazurin.utils.filters import URLFilter

from .bot import NazurinBot
from .middleware import AuthMiddleware, LoggingMiddleware
from .server import NazurinServer


class NazurinDispatcher(Dispatcher):
    def __init__(self, bot: NazurinBot):
        super().__init__(bot)
        self.bot: NazurinBot = bot
        self.middleware.setup(AuthMiddleware())
        self.middleware.setup(LoggingMiddleware())
        self.filters_factory.bind(URLFilter, event_handlers=[self.message_handlers])
        self.server = NazurinServer(bot)
        self.executor = Executor(self, skip_updates=True)
        self.executor.on_startup(self.on_startup)
        self.executor.on_shutdown(self.on_shutdown)

    def init(self):
        self.bot.init()
        self.register_message_handler(
            self.update_collection,
            URLFilter(),
            content_types=[ContentType.TEXT, ContentType.PHOTO],
        )

    def register_message_handler(self, callback, *args, **kwargs):
        return super().register_message_handler(
            self.async_task(callback), *args, **kwargs
        )

    async def on_startup(self, *_args):
        if config.ENV == "production":
            await self.bot.set_webhook(
                config.WEBHOOK_URL + config.TOKEN,
                allowed_updates=AllowedUpdates.MESSAGE,
            )
        await self.bot.on_startup()

    async def on_shutdown(self, *_args):
        await self.bot.on_shutdown()

    async def process_update(self, update: Update):
        with logger.contextualize(request=f"update:{update.update_id}"):
            return await super().process_update(update)

    def start(self):
        self.init()
        if config.ENV == "production":
            logger.info("Set webhook")
            self.executor.set_webhook(
                webhook_path="/" + config.TOKEN, web_app=self.server
            )
            # Tell aiohttp to use main thread event loop instead of creating a new one
            # otherwise bot commands will run in a different loop
            # from main thread functions and classes like Mongo and Mega.api_upload,
            # resulting in RuntimeError: Task attached to different loop
            self.executor.run_app(
                host=config.HOST,
                port=config.PORT,
                loop=asyncio.get_event_loop(),
                access_log_format=config.ACCESS_LOG_FORMAT,
            )
        else:
            # self.server.start()
            self.executor.start_polling()

    async def update_collection(self, message: Message, urls: List[str]):
        await self.bot.update_collection(urls, message)
        await message.reply("Done!")
