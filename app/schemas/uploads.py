"""Schemas for ATBDS models"""

from pydantic import BaseModel, validator

from app import config
from app.api.utils import s3_client


class Create(BaseModel):
    """Model for ATBD PDF Upload"""

    atbd_id: int
    created_by: str


class CreateReponse(BaseModel):
    """Model for ATBD PDF Upload"""

    upload_url: str
    upload_fields: dict
    upload_id: int


class Update(BaseModel):
    """Model for ATBD PDF Upload"""


class FullOutput(BaseModel):
    """Base Model for PdfUpload Output"""

    id: int
    file_path: str

    class Config:
        """Config."""

        title = "PdfUplaod"
        orm_mode = True

    @validator("file_path")
    def sign_file_path(cls, file_path):
        """Generated signed s3 url which client needs to access the files"""
        client = s3_client()
        url = client.generate_presigned_url(
            "get_object",
            Params=dict(
                Bucket=config.S3_BUCKET,
                Key=str(file_path),
                ResponseContentType="application/pdf",
            ),
            ExpiresIn=3600,
        )
        if config.APT_DEBUG:
            # localstack is available on localhost when running in dev mode
            url = url.replace("localstack", "localhost")
        return url
