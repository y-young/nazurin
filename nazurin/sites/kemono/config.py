from dataclasses import dataclass
from enum import Enum

from nazurin.config import env

PRIORITY = 10


class Site(str, Enum):
    """Site identifier of websites powered by the Kemono software."""

    KEMONO = "kemono"
    PAWCHIVE = "pawchive"


@dataclass(frozen=True)
class SiteConfig:
    """Static configuration of a website powered by the Kemono software."""

    name: str
    api_base: str
    referer: str
    web_base: str
    file_base: str
    thumbnail_base: str
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    )


SITES: dict[Site, SiteConfig] = {
    Site.KEMONO: SiteConfig(
        name="Kemono",
        api_base="https://kemono.cr/api/v1",
        referer="https://kemono.cr/",
        web_base="https://kemono.cr",
        file_base="https://n2.kemono.cr/data",
        thumbnail_base="https://img.kemono.cr/thumbnail/data",
    ),
    Site.PAWCHIVE: SiteConfig(
        name="Pawchive",
        api_base="https://pawchive.pw/api/v1",
        referer="https://pawchive.pw/",
        web_base="https://pawchive.pw",
        file_base="https://file.pawchive.pw/data",
        thumbnail_base="https://img.pawchive.pw/thumbnail/data",
        # The Pawchive file CDN blocks browser-like user agents,
        # so an identifiable one is required
        user_agent="Nazurin (+https://github.com/y-young/nazurin)",
    ),
}

COLLECTIONS: dict[Site, str] = {
    Site.KEMONO: "kemono",
    Site.PAWCHIVE: "pawchive",
}

with env.prefixed("KEMONO_"), env.prefixed("FILE_"):
    DESTINATION: str = env.str(
        "PATH",
        default="{site_name}/{service}/{username} ({user})/{title} ({id})",
    )
    FILENAME: str = env.str("NAME", default="{pretty_name}")
