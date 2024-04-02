"""Kemono.party site plugin."""

from .api import Kemono
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["Kemono", "PRIORITY", "patterns", "handle"]
