"""Nazurin database drivers and database manager."""
import importlib

from nazurin.config import DATABASE


class Database:
    """Nazurin database manager."""

    def __init__(self):
        """Dynamically load all database drivers."""
        module = importlib.import_module("nazurin.database." + DATABASE.lower())
        self.driver = getattr(module, DATABASE)
