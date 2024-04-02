"""Zerochan site plugin."""

from .api import Zerochan
from .commands import *
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["Zerochan", "PRIORITY", "patterns", "handle"]
