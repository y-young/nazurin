"""Bilibili dynamic site plugin."""
from .api import Bilibili
from .config import PRIORITY
from .interface import patterns, handle

__all__ = ['Bilibili', 'PRIORITY', 'patterns', 'handle']