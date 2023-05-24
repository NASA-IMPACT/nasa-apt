"""CRUD Operations for Upload model"""
import datetime
from pathlib import Path
from typing import Union

from sqlalchemy import exc

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import PDFUpload
from app.logs import logger  # noqa
from app.schemas.uploads import Create, FullOutput, Update

from fastapi import HTTPException


class CRUDPdfUploads(CRUDBase[PDFUpload, FullOutput, Create, Update]):
    """CRUDUploads."""

    def get(self, db: DbSession, pdf_id: int, filters={}) -> PDFUpload:
        """Query a single PDF Upload."""
        query = db.query(PDFUpload).filter(PDFUpload.id == pdf_id).filter_by(**filters)

        try:
            return query.one()
        except exc.SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=404, detail=f"No PDF file found for id/alias: {pdf_id}"
            )

    def create(
        self,
        db: DbSession,
        *,
        obj_in: Create,
        commit=True,
    ) -> PDFUpload:
        """Creates a new PDF Upload."""

        atbd_id = obj_in.atbd_id
        upload_path = Path(str(obj_in.atbd_id)) / "uploads"
        file_name = f"atbd_{atbd_id}_{int(datetime.datetime.now().timestamp())}.pdf"
        file_path = upload_path / file_name
        pdf_upload = PDFUpload(
            **obj_in.dict(),
            file_path=str(file_path),
        )
        db.add(pdf_upload)
        if commit:
            db.commit()
            db.refresh(pdf_upload)
        logger.info(f"Creating PDF upload: {pdf_upload}")
        return pdf_upload


crud_uploads = CRUDPdfUploads(PDFUpload)
