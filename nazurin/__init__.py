from nazurin import config
from nazurin.utils.logging import configure_logging

from .bot import NazurinBot
from .dispatcher import NazurinDispatcher

configure_logging()

bot = NazurinBot(token=config.TOKEN, proxy=config.PROXY)
dp = NazurinDispatcher(bot)

__all__ = ["bot", "dp"]
