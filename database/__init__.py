import importlib
from config import DATABASE

class Database(object):
    def __init__(self):
        module = importlib.import_module('database.' + DATABASE.lower())
        self.driver = getattr(module, DATABASE)
