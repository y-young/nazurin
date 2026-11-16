import os
from datetime import datetime, timezone
from http import HTTPStatus
from mimetypes import guess_type
from typing import Any, ClassVar, TypeVar
from urllib.parse import quote

from nazurin.models import Caption, Illust, Image
from nazurin.models.file import File
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from .config import DESTINATION, FILENAME, SITES, Site, SiteConfig

T = TypeVar("T")


class KemonoRequest:
    """Custom request class for Kemono API with built-in headers and JSON handling."""

    DEFAULT_HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "text/css",
        "Accept-Language": "en-US;q=1.0",
    }

    def __init__(self, api_base: str, referer: str, user_agent: str):
        self.api_base = api_base
        self.headers = {
            "User-Agent": user_agent,
            **self.DEFAULT_HEADERS,
            "Referer": referer,
        }

    async def get(
        self,
        path: str,
        response_type: type[T],
    ) -> T:
        """Make a GET request and return the decoded JSON response.

        Args:
            path: Relative path appended to the API base URL.
            response_type: Expected response type for generic type inference.
        """
        url = f"{self.api_base}/{path}"
        async with (
            Request() as session,
            session.get(url, headers=self.headers) as response,
        ):
            if response.status == HTTPStatus.FORBIDDEN:
                content = await response.text()
                raise NazurinError(f"403 Forbidden: {content[:100]}")
            response.raise_for_status()
            return await response.json(content_type=None)


class KemonoIllust(Illust):
    """Illust that downloads files with the user agent of the corresponding site."""

    def __init__(self, *args, site_config: SiteConfig, **kwargs):
        super().__init__(*args, **kwargs)
        self.site_config = site_config

    async def download(self, **kwargs):
        headers = {
            "User-Agent": self.site_config.user_agent,
            "Referer": self.site_config.referer,
            **kwargs.pop("headers", {}),
        }
        await super().download(headers=headers, **kwargs)


class Kemono:
    _clients: ClassVar[dict[Site, KemonoRequest]] = {}

    def __init__(self, site: Site = Site.KEMONO):
        self.site(site)

    def site(self, site: Site = Site.KEMONO) -> "Kemono":
        """Select the website to fetch from."""
        self._site = site
        self._site_config = SITES[site]
        return self

    @property
    def client(self) -> KemonoRequest:
        if self._site not in self._clients:
            self._clients[self._site] = KemonoRequest(
                api_base=self._site_config.api_base,
                referer=self._site_config.referer,
                user_agent=self._site_config.user_agent,
            )
        return self._clients[self._site]

    @network_retry
    async def get_post(self, service: str, user_id: str, post_id: str) -> dict:
        """Fetch a post."""
        api = f"{service}/user/{user_id}/post/{post_id}"
        data = await self.client.get(api, dict[str, Any])
        post = data.get("post", data)
        username = await self.get_username(service, user_id)
        post["username"] = username
        return post

    @network_retry
    async def get_post_revision(
        self,
        service: str,
        user_id: str,
        post_id: str,
        revision_id: str,
    ) -> dict:
        """Fetch a post revision."""
        api = f"{service}/user/{user_id}/post/{post_id}/revisions"
        revisions = await self.client.get(api, list[dict[str, Any]])
        post = None
        for revision in revisions:
            if str(revision["revision_id"]) == revision_id:
                post = revision
                break
        if not post:
            raise NazurinError("Post revision not found")
        username = await self.get_username(service, user_id)
        post["username"] = username
        return post

    @network_retry
    async def get_username(self, service: str, user_id: str) -> str:
        path = f"{service}/user/{user_id}/profile"
        profile = await self.client.get(path, dict[str, Any])
        if isinstance(profile, list) and len(profile) > 0:
            return profile[0].get("name", "")
        return profile.get("name", "")

    async def fetch(
        self,
        service: str,
        user_id: str,
        post_id: str,
        revision_id: str | None,
    ) -> Illust:
        if revision_id:
            post = await self.get_post_revision(service, user_id, post_id, revision_id)
        else:
            post = await self.get_post(service, user_id, post_id)
        caption = self.build_caption(post)

        images: list[Image] = []
        download_files: list[File] = []
        files: list[dict[str, Any]] = [post["file"]] if post.get("file") else []
        files += post.get("attachments", [])

        if not files:
            raise NazurinError("No files found")

        image_index = 0
        for file in files:
            path: str = file["path"]
            file_name: str = file.get("name", "")
            # Whether the original file is not archived,
            # in which case only the preview thumbnail is available
            preview_only = bool(file.get("preview_only"))

            encoded_filename = quote(file_name)
            url = f"{self._site_config.file_base}{path}?f={encoded_filename}"

            # Handle non-image files
            if not self.is_image(path):
                if post["service"] == "dlsite" and path.endswith(".html"):
                    # HTML files from DLSite seems useless
                    continue
                if preview_only:
                    # No preview available for non-image files
                    logger.warning(
                        "Skip file not archived: {} ({})",
                        file_name,
                        self.get_url(post),
                    )
                    continue
                destination, filename = self.get_storage_dest(post, file_name, path)
                download_files.append(File(filename, url, destination))
                continue

            # Handle images
            destination, filename = self.get_storage_dest(
                post,
                f"{image_index} - {file_name}",
                path,
            )

            thumbnail = f"{self._site_config.thumbnail_base}{path}"

            if preview_only:
                # Fall back to the preview thumbnail
                logger.warning(
                    "Image not archived, falling back to preview: {} ({})",
                    file_name,
                    self.get_url(post),
                )
                url = thumbnail

            images.append(
                Image(
                    filename,
                    url,
                    destination,
                    thumbnail,
                ),
            )
            image_index += 1

        identifier = filter(lambda x: x, [service, user_id, post_id, revision_id])
        return KemonoIllust(
            "_".join(identifier),
            images,
            caption,
            post,
            download_files,
            site_config=self._site_config,
        )

    def get_storage_dest(
        self,
        post: dict,
        pretty_name: str,
        path: str,
    ) -> tuple[str, str]:
        """
        Format destination and filename.
        """

        def parse_time(time_str: Any) -> datetime:
            default_time = datetime(1970, 1, 1, tzinfo=timezone.utc)
            if not time_str or not isinstance(time_str, str):
                return default_time
            try:
                return fromisoformat(time_str).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                return default_time

        added = parse_time(post.get("added"))
        edited = parse_time(post.get("edited") or post.get("added"))
        published = parse_time(post.get("published") or post.get("added"))
        pretty_name, _ = os.path.splitext(pretty_name)
        filename, extension = os.path.splitext(path)
        context = {
            **post,
            "site": self._site.value,
            "site_name": self._site_config.name,
            # Default filename provided by site, without extension
            "filename": filename,
            # Filename provided by author, with extension
            "pretty_name": pretty_name,
            "added": added,
            "edited": edited,
            "published": published,
            "extension": extension,
        }
        filename = FILENAME.format_map(context)
        return (DESTINATION.format_map(context), filename + extension)

    def get_url(self, post: dict) -> str:
        web_base = self._site_config.web_base
        url = f"{web_base}/{post['service']}/user/{post['user']}/post/{post['id']}"
        revision = post.get("revision_id")
        if revision:
            url += f"/revision/{post['revision_id']}"
        return url

    def build_caption(self, post: dict[str, Any]) -> Caption:
        return Caption(
            {
                "title": post["title"],
                "author": "#" + post["username"],
                "url": self.get_url(post),
            },
        )

    @staticmethod
    def is_image(path: str) -> bool:
        """Check if path is an image by mimetype."""
        mimetype = guess_type(path)[0]
        return mimetype is not None and mimetype.startswith("image")
