"""Telegraph site plugin."""

from .api import Telegraph
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Telegraph", "handle", "patterns"]
