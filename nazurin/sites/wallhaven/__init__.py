"""Wallhaven site plugin."""

from .api import Wallhaven
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Wallhaven", "handle", "patterns"]
