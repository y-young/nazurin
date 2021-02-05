from aiogram import Dispatcher, executor
from aiogram.types import AllowedUpdates
from aiogram.utils.executor import start_webhook

from nazurin import config
from nazurin.utils import logger
from nazurin.utils.filters import URLFilter

from .bot import NazurinBot
from .middleware import AuthMiddleware

class NazurinDispatcher(Dispatcher):
    def __init__(self, bot: NazurinBot):
        super().__init__(bot)
        self.middleware.setup(AuthMiddleware())
        self.filters_factory.bind(URLFilter,
                                  event_handlers=[self.message_handlers])

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
