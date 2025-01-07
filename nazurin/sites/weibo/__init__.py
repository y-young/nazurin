"""Sina Weibo site plugin."""

from .api import Weibo
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Weibo", "handle", "patterns"]
