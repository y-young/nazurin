"""Kemono.party site plugin."""

from .api import Kemono
from .config import PRIORITY
from .interface import handle, patterns

__all__ = ["PRIORITY", "Kemono", "handle", "patterns"]
