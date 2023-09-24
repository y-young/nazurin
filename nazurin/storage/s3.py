# -*- coding: utf-8 -*-
import asyncio
import mimetypes
from typing import List

from minio import Minio

from nazurin.config import env
from nazurin.models import File
from nazurin.utils import logger

S3_ENDPOINT = env.str("S3_ENDPOINT", default="s3.amazonaws.com")
S3_ACCESS_KEY = env.str("S3_ACCESS_KEY")
S3_SECRET_KEY = env.str("S3_SECRET_KEY")
S3_SECURE = env.bool("S3_SECURE", default=True)
S3_REGION = env.str("S3_REGION", default="null")
S3_BUCKET = env.str("S3_BUCKET", default="nazurin")


class S3:
    """S3 driver"""

    client = Minio(
        endpoint=S3_ENDPOINT,
        access_key=S3_ACCESS_KEY,
        secret_key=S3_SECRET_KEY,
        region=S3_REGION,
        secure=S3_SECURE,
    )

    async def check_bucket(self):
        if not S3.client.bucket_exists(S3_BUCKET):
            S3.client.make_bucket(S3_BUCKET)
            logger.info("Bucket created: {}", S3_BUCKET)

    async def upload(self, file: File):
        S3.client.fput_object(
            bucket_name=S3_BUCKET,
            object_name=file.name,
            file_path=file.path,
            content_type=mimetypes.guess_type(file.name)[0]
            or "application/octet-stream",
            metadata={
                "destination": file.destination,
            },
        )

    async def store(self, files: List[File]):
        await self.check_bucket()

        tasks = [self.upload(file) for file in files]
        await asyncio.gather(*tasks)

        return True
