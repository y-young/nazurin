"""Xfolio site plugin."""

from .api import Xfolio
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Xfolio", "handle", "patterns"]
