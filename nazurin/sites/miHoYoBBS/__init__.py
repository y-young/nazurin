"""Plugin for China miHoYo BBS"""
from .api import miHoYoBBS
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ['miHoYoBBS', 'PRIORITY', 'patterns', 'handle']