"""Artstation site plugin."""

from .api import Artstation
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Artstation", "handle", "patterns"]
