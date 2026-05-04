from __future__ import annotations

import asyncio
from typing import Any

import boto3

from app.utils.config import get_settings


class StorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.bucket_name = settings.s3_bucket_name
        self.presigned_expiry = settings.presigned_url_expiry_seconds
        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

    async def create_upload_url(self, key: str, content_type: str) -> str:
        return await asyncio.to_thread(
            self.client.generate_presigned_url,
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=self.presigned_expiry,
        )

    async def download_file_bytes(self, key: str) -> bytes:
        def _download() -> bytes:
            response: dict[str, Any] = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()

        return await asyncio.to_thread(_download)


storage_service = StorageService()
