from nazurin import config

from .bot import NazurinBot
from .dispatcher import NazurinDispatcher

bot = NazurinBot(token=config.TOKEN, proxy=config.PROXY)
dp = NazurinDispatcher(bot)

__all__ = ['bot', 'dp']
