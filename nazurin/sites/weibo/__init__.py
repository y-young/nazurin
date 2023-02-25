"""Sina Weibo site plugin."""
from .api import Weibo
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["Weibo", "PRIORITY", "patterns", "handle"]
