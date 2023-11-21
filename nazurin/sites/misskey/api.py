import os
import shlex
import subprocess
from pathlib import Path
from typing import List, Tuple

from aiohttp.client_exceptions import ClientResponseError
from pydantic import ValidationError

from nazurin.models import Caption, Illust, Image, Ugoira
from nazurin.models.file import File
from nazurin.sites.misskey.models import File as NoteFile
from nazurin.sites.misskey.models import Note
from nazurin.utils import Request, logger
from nazurin.utils.decorators import async_wrap, network_retry
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import fromisoformat

from .config import DESTINATION, FILENAME


class Misskey:
    @network_retry
    async def get_note(self, site_url: str, note_id: str) -> Note:
        """Fetch a note from a Misskey instance."""
        api = f"https://{site_url}/api/notes/show"
        json = {"noteId": note_id}

        async with Request() as request:
            async with request.post(url=api, json=json) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None

                data = await response.json()
                try:
                    return Note.model_validate(data)
                except ValidationError as err:
                    raise NazurinError(err) from None

    def build_caption(self, note: Note, site_url: str) -> Caption:
        url = f"https://{site_url}/notes/{note.id}"
        caption = {
            "url": url,
            "author": f"{note.user.name} #{note.user.username}",
            "text": note.text,
        }
        # URL from the original instance
        if note.uri is not None:
            caption["original_url"] = note.uri
        return Caption(caption)

    async def get_video(self, file: NoteFile, destination: str, filename: str) -> File:
        file_type = file.type
        if file_type in ["video/mp4", "image/gif"]:
            video = File(filename, file.url, destination)
        else:

            @async_wrap
            def convert(config: File, output: File):
                config_path = Path(config.path).as_posix()
                # Copy video and audio streams
                args = [
                    "ffmpeg",
                    "-i",
                    config_path,
                    "-vcodec",
                    "copy",
                    "-acodec",
                    "copy",
                    "-y",
                    output.path,
                ]
                cmd = shlex.join(args)
                logger.info("Calling FFmpeg with command: {}", cmd)
                try:
                    output = subprocess.check_output(
                        args, stderr=subprocess.STDOUT, shell=False
                    )
                except subprocess.CalledProcessError as error:
                    logger.error(
                        "FFmpeg failed with code {}, output:\n {}",
                        error.returncode,
                        error.output.decode(),
                    )
                    raise NazurinError("Failed to convert ugoira to mp4.") from None

            ori_video = File(filename, file.url)
            async with Request() as session:
                await ori_video.download(session)
            filename, _ = os.path.splitext(filename)
            video = File(filename + ".mp4", "", destination)
            await convert(ori_video, video)
        return video

    async def parse_note(self, note: Note, site_url: str) -> Illust:
        """Build caption and get images."""
        # Build note caption
        caption = self.build_caption(note, site_url)

        images: List[Image] = []
        files: List[File] = []
        note_files = note.files
        for index, file in enumerate(note_files):
            if not file.url:
                continue
            destination, filename = self.get_storage_dest(note, file, index)
            file_type = file.type
            if file_type.startswith("image") and not file_type.endswith("gif"):
                images.append(
                    Image(
                        filename,
                        file.url,
                        destination,
                        file.thumbnailUrl,
                        file.size,
                        file.properties.width,
                        file.properties.height,
                    )
                )
            elif file_type.startswith("video") or file_type.endswith("gif"):
                return Ugoira(
                    await self.get_video(file, destination, filename),
                    caption,
                    note.model_dump(),
                )

        return Illust(images, caption, note.model_dump(), files)

    async def fetch(self, site_url: str, note_id: str) -> Illust:
        note = await self.get_note(site_url, note_id)
        return await self.parse_note(note, site_url)

    @staticmethod
    def get_storage_dest(note: Note, file: NoteFile, index: int) -> Tuple[str, str]:
        """
        Format destination and filename.
        """
        created_at = fromisoformat(note.createdAt)
        filename, extension = os.path.splitext(file.name)
        context = {
            "user": note.user.model_dump(),
            **file.properties.model_dump(),
            "md5": file.md5,
            # Human-friendly filename, without extension
            "filename": filename,
            "index": index,
            "id": note.id,
            "created_at": created_at,
            "extension": extension,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + extension,
        )
