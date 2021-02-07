from aiogram import Dispatcher, executor
from aiogram.types import AllowedUpdates
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
        self.server.on_shutdown.append(self.on_shutdown)
        self.executor = Executor(self)

    def register_message_handler(self, callback, *args, **kwargs):
        return super().register_message_handler(self.async_task(callback),
                                                *args, **kwargs)

    async def on_startup(self, dp):
        await self.bot.set_webhook(config.WEBHOOK_URL + config.TOKEN,
                                   allowed_updates=AllowedUpdates.MESSAGE)

    async def on_shutdown(self, dp):
        await self.bot.delete_webhook()  # TODO

    def start(self):
        self.bot.init()
        # TODO
        if config.ENV == 'production':
            logger.info('Set webhook')
            self.executor.set_webhook(webhook_path='/' + config.TOKEN,
                                      web_app=self.server)
            self.executor.run_app(host="0.0.0.0", port=config.PORT)
        else:
            # self.server.start()
            executor.start_polling(self, skip_updates=True)
