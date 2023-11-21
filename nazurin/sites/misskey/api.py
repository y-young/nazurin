import os
from datetime import datetime
from pathlib import Path
import shlex
import subprocess
from typing import List, Tuple

from aiohttp.client_exceptions import ClientResponseError
from nazurin.models import Caption, Illust, Image, Ugoira
from nazurin.models.file import File
from nazurin.utils import Request, logger
from nazurin.utils.decorators import network_retry, async_wrap
from nazurin.utils.exceptions import NazurinError

from .config import DESTINATION, FILENAME


class Misskey:
    def check_res_json(self, data: dict) -> bool:
        note_required_fields = ["id", "user", "text", "createdAt", "files"]
        for f in note_required_fields:
            if f not in data:
                return False
        user = data["user"]
        user_required_fileds = ["username", "name"]
        for f in user_required_fileds:
            if f not in user:
                return False
        files = data["files"]
        file_required_fields = ["name", "type", "url", "thumbnailUrl", "size", "properties"]
        for file in files:
            for f in file_required_fields:
                if f not in file:
                    return False
        return True
    
    @network_retry
    async def get_note(self, site_url: str, note_id: str) -> dict:
        """Fetch a note from a Misskey instance."""
        api = f"https://{site_url}/api/notes/show"
        json = {
            "noteId": note_id
        }

        async with Request() as request:
            async with request.post(url=api, json=json) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as err:
                    raise NazurinError(err) from None
                data = await response.json()
                
                # check JSON format
                if not self.check_res_json(data):
                    raise NazurinError("Invalid JSON format.")
                
                return data

    def build_caption(self, note: dict, site_url: str) -> Caption:
        url = f"https://{site_url}/notes/{note['id']}"
        # URL from the original instance
        if note["uri"] is None:
            return Caption(
                {
                    "url": url,
                    "author": f"{note['user']['username']} #{note['user']['name']}",
                    "text": note["text"],
                }
            )
        else:
            return Caption(
                {
                    "url": url,
                    "original_url": note["uri"],
                    "author": f"{note['user']['username']} #{note['user']['name']}",
                    "text": note["text"],
                }
            )

    async def get_video(self, file: dict, destination: str, filename: str) -> File:
        if file["type"] == "video/mp4" or file["type"] == "image/gif":
            video = File(filename, file["url"], destination)
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
                    raise NazurinError(
                        "Failed to convert ugoira to mp4.") from None

            ori_video = File(filename, file["url"])
            async with Request() as session:
                await ori_video.download(session)
            filename, _ = os.path.splitext(filename)
            video = File(filename + ".mp4", "", destination)
            await convert(ori_video, video)
        return video

    async def parse_note(self, note: dict, site_url: str) -> Illust:
        """Build caption and get images."""
        # Build note caption
        caption = self.build_caption(note, site_url)

        images: List[Image] = []
        files: List[File] = []
        file_dict = note["files"]
        for file in file_dict:
            destination, filename = self.get_storage_dest(note, file["name"])
            if file["type"].startswith("image") and not file["type"].endswith("gif"):
                images.append(
                    Image(
                        filename,
                        file["url"],
                        destination,
                        file["thumbnailUrl"],
                        file["size"],
                        file["properties"]["width"],
                        file["properties"]["height"],
                    )
                )
            elif file["type"].startswith("video") or file["type"].endswith("gif"):
                return Ugoira(await self.get_video(file, destination, filename), caption, note)

        return Illust(images, caption, note, files)

    async def fetch(self, site_url: str, post_id: str) -> Illust:
        note = await self.get_note(site_url, post_id)
        return await self.parse_note(note, site_url)

    @staticmethod
    def get_storage_dest(note: dict, filename: str) -> Tuple[str, str]:
        """
        Format destination and filename.
        """
        # remove 'Z' to fit datetime.fromisoformat's needs
        created_at = datetime.fromisoformat(note["createdAt"][:-1])
        filename, extension = os.path.splitext(filename)
        context = {
            **note,
            # Human-friendly filename, without extension
            "filename": filename,
            "created_at": created_at,
            "extension": extension,
        }
        return (
            DESTINATION.format_map(context),
            FILENAME.format_map(context) + extension,
        )
