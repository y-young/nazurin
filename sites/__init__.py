import importlib
import glob
import sys
import os

sys.path.append('../')

class SiteManager(object):
    def __init__(self):
        self.sites = dict()
        self.commands = list()
        self.load()

    def load(self):
        module_paths = glob.glob('sites/*/')
        for path in module_paths:
            module_name = os.path.basename(os.path.normpath(path))
            if module_name.startswith('__'):
                continue
            module = importlib.import_module('sites.' + module_name)
            self.sites[module_name.lower()] = getattr(module, module_name)
            if hasattr(module, 'commands'):
                self.commands += getattr(module, 'commands')

    def api(self, site):
        return self.sites[site]

    def register_commands(self, dispatcher):
        for command in self.commands:
            dispatcher.add_handler(command)
