"""Bilibili dynamic site plugin."""

from .api import Bilibili
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["Bilibili", "PRIORITY", "patterns", "handle"]
