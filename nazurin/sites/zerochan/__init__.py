"""Zerochan site plugin."""

from .api import Zerochan
from .commands import *  # noqa: F403
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Zerochan", "handle", "patterns"]
