"""Bilibili dynamic site plugin."""
from .api import Bilibili
from .interface import PRIORITY, patterns, handle

__all__ = ['Bilibili', 'PRIORITY', 'patterns', 'handle']