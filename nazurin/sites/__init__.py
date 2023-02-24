"""Nazurin site plugins & plugin manager."""
from glob import glob
from importlib import import_module
from os import path
from re import search
from typing import List

from nazurin.models import Illust
from nazurin.utils import logger
from nazurin.utils.helpers import snake_to_pascal

class SiteManager:
    """Site plugin manager."""
    def __init__(self):
        """Initialize."""
        self.sites = {}
        self.sources = []

    def load(self):
        """Dynamically load all site plugins."""
        module_paths = glob('nazurin/sites/*/')
        for module_path in module_paths:
            module_name = path.basename(path.normpath(module_path))
            if module_name.startswith('__'):
                continue

            module = import_module('nazurin.sites.' + module_name)
            # Store site API class
            self.sites[module_name.lower()] = getattr(
                module, snake_to_pascal(module_name))()
            if hasattr(module, 'patterns') and hasattr(module, 'handle'):
                PRIORITY = getattr(module, 'PRIORITY')
                patterns = getattr(module, 'patterns')
                handle = getattr(module, 'handle')
                self.sources.append((PRIORITY, patterns, handle, module_name))
            self.sources.sort(key=lambda s: s[0], reverse=True)
        logger.info("Loaded {} sites", len(self.sites))

    def api(self, site):
        return self.sites[site]

    def match(self, urls: List[str]):
        sources = self.sources
        urls = str.join(',', urls)
        result = None
        matched_priority = 0

        for interface in sources:
            priority, patterns, handle, site_name = interface
            if priority < matched_priority:
                break
            for pattern in patterns:
                match = search(pattern, urls)
                if match:
                    result = {
                        'match': match,
                        'site': site_name,
                        'handler': handle
                    }
                    matched_priority = priority
                    break

        if not result:
            return False
        return result

    async def handle_update(self, result) -> Illust:
        handle = result['handler']
        return await handle(result['match'])
