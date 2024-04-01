"""Artstation site plugin."""

from .api import Artstation
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["Artstation", "PRIORITY", "patterns", "handle"]
