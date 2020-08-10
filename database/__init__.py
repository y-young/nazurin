"""Nazurin database drivers and database manager."""
import importlib
from config import DATABASE

class Database(object):
    """Nazurin database manager."""

    def __init__(self):
        """Dynamically load all database drivers."""
        module = importlib.import_module('database.' + DATABASE.lower())
        self.driver = getattr(module, DATABASE)
