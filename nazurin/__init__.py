from nazurin.utils.logging import configure_logging

from .bot import NazurinBot
from .dispatcher import NazurinDispatcher

configure_logging()

bot = NazurinBot()
dp = NazurinDispatcher(bot)

__all__ = ["bot", "dp"]
