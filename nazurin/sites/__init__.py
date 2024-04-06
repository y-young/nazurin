"""Nazurin site plugins & plugin manager."""

import re
from glob import glob
from importlib import import_module
from os import path
from typing import Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict

from nazurin.models import Illust
from nazurin.models.document import Document
from nazurin.utils import logger
from nazurin.utils.helpers import snake_to_pascal

HandlerResult = Tuple[Illust, Document]
SourceHandler = Callable[[re.Match], HandlerResult]


class Source(BaseModel):
    priority: int
    patterns: List[str]
    handler: SourceHandler
    name: str


class MatchResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    match: re.Match
    source: Source


class SiteManager:
    """Site plugin manager."""

    def __init__(self):
        self.sites: Dict[str, object] = {}
        self.sources: List[Source] = []

    def load(self):
        """Dynamically load all site plugins."""
        module_paths = glob("nazurin/sites/*/")
        for module_path in module_paths:
            module_name = path.basename(path.normpath(module_path))
            if module_name.startswith("__"):
                continue

            module = import_module("nazurin.sites." + module_name)
            # Store site API class
            self.sites[module_name.lower()] = getattr(
                module,
                snake_to_pascal(module_name),
            )()
            if hasattr(module, "patterns") and hasattr(module, "handle"):
                priority = module.PRIORITY
                patterns = module.patterns
                handle = module.handle
                self.sources.append(
                    Source(
                        priority=priority,
                        patterns=patterns,
                        handler=handle,
                        name=module_name,
                    ),
                )
            self.sources.sort(key=lambda s: s.priority, reverse=True)
        logger.info("Loaded {} sites", len(self.sites))

    def api(self, site: str):
        return self.sites[site]

    def match(self, urls: List[str]) -> Optional[MatchResult]:
        sources = self.sources
        urls = str.join(",", urls)
        result: Optional[MatchResult] = None
        matched_priority = 0

        for source in sources:
            if source.priority < matched_priority:
                break
            for pattern in source.patterns:
                match = re.search(pattern, urls)
                if match:
                    result = MatchResult(match=match, source=source)
                    matched_priority = source.priority
                    break

        return result

    async def handle_update(self, result: MatchResult) -> HandlerResult:
        handle = result.source.handler
        return await handle(result.match)
