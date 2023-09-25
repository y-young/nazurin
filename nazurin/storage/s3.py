import asyncio
import mimetypes
from typing import List

from minio import Minio

from nazurin.config import env
from nazurin.models import File
from nazurin.utils import logger
from nazurin.utils.decorators import async_wrap

with env.prefixed("S3_"):
    ENDPOINT = env.str("ENDPOINT", default="s3.amazonaws.com")
    ACCESS_KEY = env.str("ACCESS_KEY")
    SECRET_KEY = env.str("SECRET_KEY")
    SECURE = env.bool("SECURE", default=True)
    REGION = env.str("REGION", default=None)
    BUCKET = env.str("BUCKET", default="nazurin")


class S3:
    """S3 driver"""

    client = Minio(
        endpoint=ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        region=REGION,
        secure=SECURE,
    )

    @async_wrap
    async def check_bucket(self):
        if not S3.client.bucket_exists(BUCKET):
            S3.client.make_bucket(BUCKET)
            logger.info("Bucket created: {}", BUCKET)

    @async_wrap
    async def upload(self, file: File):
        S3.client.fput_object(
            bucket_name=BUCKET,
            object_name=f"{file.destination}/{file.name}",
            file_path=file.path,
            content_type=mimetypes.guess_type(file.name)[0]
            or "application/octet-stream",
        )

    async def store(self, files: List[File]):
        await self.check_bucket()

        tasks = [self.upload(file) for file in files]
        await asyncio.gather(*tasks)

        return True
