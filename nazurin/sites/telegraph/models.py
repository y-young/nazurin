from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import aiofiles
import aiofiles.os
from aiohttp import ClientError
from PIL import Image as PILImage

from nazurin.config import MAX_PARALLEL_DOWNLOAD, TEMP_DIR
from nazurin.models import Caption, File, Illust, Image
from nazurin.utils import Request, logger
from nazurin.utils.decorators import async_wrap
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import (
    FILENAME_MAX_LENGTH,
    ensure_existence_async,
    sanitize_filename,
)

from .renderer import (
    SAFE_MEDIA_SCHEMES,
    ImageReference,
    TelegraphRenderer,
    collect_image_references,
    safe_url,
)

TRUSTED_IMAGE_SUFFIXES = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}
PILLOW_EXTENSIONS = {
    "BMP": ".bmp",
    "GIF": ".gif",
    "JPEG": ".jpg",
    "PNG": ".png",
    "TIFF": ".tiff",
    "WEBP": ".webp",
}
PATH_HASH_LENGTH = 12


def build_archive_name(page: dict) -> str:
    """Build a readable storage directory name using project filename rules."""
    title = sanitize_filename(page["title"]).strip(" .") or "Untitled"
    path_hash = hashlib.sha256(page["path"].encode()).hexdigest()[:PATH_HASH_LENGTH]
    suffix = f" ({path_hash})"
    title = title[: FILENAME_MAX_LENGTH - len(suffix)].rstrip()
    return title + suffix


class TelegraphIllust(Illust):
    """A Telegraph page prepared as a directory of local files."""

    def __init__(
        self,
        raw_response: dict,
        page: dict,
        source_url: str,
        destination: str,
    ):
        page_url = safe_url(page.get("url"), source_url, SAFE_MEDIA_SCHEMES)
        page_url = page_url or source_url
        content_json = json.dumps(
            page["content"],
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        metadata = {
            **page,
            "canonical_path": page["path"],
            "content_sha256": hashlib.sha256(content_json.encode()).hexdigest(),
            "source_url": source_url,
        }
        caption = Caption(
            {
                "title": page["title"],
                "author": page.get("author_name"),
                "url": page_url,
            },
        )
        self.article_file = File("article.html")
        self.article_file.destination = destination
        self.page_file = File("page.json")
        self.page_file.destination = destination
        super().__init__(
            id=page["path"],
            caption=caption,
            metadata=metadata,
            files=[self.article_file, self.page_file],
        )
        self.raw_response = raw_response
        self.page = page
        self.source_url = source_url
        self.destination = destination
        self.archive_name = build_archive_name(page)
        self.image_references = collect_image_references(
            page["content"],
            page_url,
        )
        self.asset_failures: list[dict[str, str | int]] = []
        self._workspace: str | None = None
        self._prepared = False
        self._prepare_lock = asyncio.Lock()

    async def download(self, **_kwargs):
        if await self._is_prepared():
            return
        async with self._prepare_lock:
            if await self._is_prepared():
                return
            await self._reset_workspace()
            try:
                self._create_workspace()
                await self._write_json()
                image_paths = await self._download_images()
                await self._write_article(image_paths)
                self._prepared = True
            except OSError as error:
                await self._reset_workspace()
                raise NazurinError("Failed to prepare Telegraph archive") from error
            except Exception:
                await self._reset_workspace()
                raise

    async def _is_prepared(self) -> bool:
        if not self._prepared:
            return False
        for file in self.all_files:
            if not await file.exists():
                return False
        return True

    def _create_workspace(self):
        try:
            archive_dir = Path(TEMP_DIR, "Telegraph", self.archive_name)
            archive_dir.mkdir(parents=True, exist_ok=True)
            self._workspace = tempfile.mkdtemp(
                prefix="work-",
                dir=archive_dir,
            )
        except OSError as error:
            raise NazurinError("Failed to create Telegraph workspace") from error
        self.article_file.local_path = Path(self._workspace, "article.html")
        self.page_file.local_path = Path(self._workspace, "page.json")

    async def _write_json(self):
        content = json.dumps(self.raw_response, ensure_ascii=False, indent=2) + "\n"
        await self._atomic_write(self.page_file.path, content)

    async def _write_article(self, image_paths: dict[int, str]):
        renderer = TelegraphRenderer(self.page, self.source_url, image_paths)
        await self._atomic_write(self.article_file.path, renderer.render())

    async def _download_images(self) -> dict[int, str]:
        downloadable = [
            reference for reference in self.image_references if reference.url
        ]
        semaphore = asyncio.Semaphore(MAX_PARALLEL_DOWNLOAD)
        async with Request() as session:

            async def bounded_download(asset_index: int, reference: ImageReference):
                async with semaphore:
                    return await self._download_image(
                        session,
                        asset_index,
                        reference,
                    )

            results = await asyncio.gather(
                *[
                    bounded_download(asset_index, reference)
                    for asset_index, reference in enumerate(downloadable, start=1)
                ],
            )

        self.images = [image for image, _ in results if image is not None]
        return {
            occurrence: PurePosixPath("assets", image.name).as_posix()
            for image, occurrence in results
            if image is not None
        }

    async def _download_image(
        self,
        session: Request,
        asset_index: int,
        reference: ImageReference,
    ) -> tuple[Image | None, int]:
        assert self._workspace is not None
        assert reference.url is not None
        suffix = Path(urlsplit(reference.url).path).suffix.lower()
        suffix = suffix if suffix in TRUSTED_IMAGE_SUFFIXES else ".download"
        name = f"{asset_index:03d}{suffix}"
        local_path = Path(self._workspace, "assets", name)
        image = Image(name, reference.url, local_path=local_path)
        image.destination = str(PurePosixPath(self.destination, "assets"))
        try:
            await image.download(session)
            detected_suffix = await async_wrap(self._detect_extension)(image.path)
            final_name = f"{asset_index:03d}{detected_suffix}"
            if final_name != image.name:
                final_path = Path(self._workspace, "assets", final_name)
                await aiofiles.os.replace(image.path, final_path)
                image.name = final_name
                image.local_path = final_path
            return image, reference.occurrence
        except (ClientError, asyncio.TimeoutError, NazurinError) as error:
            if await aiofiles.os.path.exists(image.path):
                await aiofiles.os.remove(image.path)
            self.asset_failures.append(
                {
                    "occurrence": reference.occurrence,
                    "url": reference.url,
                    "error": str(error),
                },
            )
            logger.warning(
                "Failed to download Telegraph image {}: {}",
                reference.url,
                error,
            )
            return None, reference.occurrence

    @staticmethod
    def _detect_extension(path: str) -> str:
        with PILImage.open(path) as image:
            extension = PILLOW_EXTENSIONS.get(image.format or "")
        if not extension:
            raise NazurinError("Unsupported Telegraph image format")
        return extension

    @staticmethod
    async def _atomic_write(path: str, content: str):
        await ensure_existence_async(os.path.dirname(path))
        temporary = path + ".tmp"
        try:
            async with aiofiles.open(temporary, "w", encoding="utf-8") as file:
                await file.write(content)
            await aiofiles.os.replace(temporary, path)
        except OSError as error:
            if await aiofiles.os.path.exists(temporary):
                await aiofiles.os.remove(temporary)
            raise NazurinError("Failed to write Telegraph archive") from error

    async def _reset_workspace(self):
        workspace = Path(self._workspace) if self._workspace else None
        if workspace and await aiofiles.os.path.exists(workspace):
            await async_wrap(shutil.rmtree)(workspace, ignore_errors=True)
            for directory in (workspace.parent, workspace.parent.parent):
                try:
                    await aiofiles.os.rmdir(directory)
                except OSError:
                    break
        self._workspace = None
        self.article_file.local_path = None
        self.page_file.local_path = None
        self.images = []
        self.asset_failures = []
        self._prepared = False
