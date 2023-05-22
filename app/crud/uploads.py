"""CRUD Operations for Upload model"""
from typing import Union

from sqlalchemy import exc

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import PDFUpload
from app.schemas.uploads import Create, FullOutput, Update

from fastapi import HTTPException


class CRUDPdfUploads(CRUDBase[PDFUpload, FullOutput, Create, Update]):
    """CRUDUploads."""

    def get(self, db: DbSession, pdf_id: int, filters={}) -> Union[PDFUpload, None]:
        """Query a single PDF Upload."""
        query = db.query(PDFUpload).filter(PDFUpload.id == pdf_id).filter_by(**filters)

        try:
            return query.one()
        except exc.SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=404, detail=f"No data found for id/alias: {pdf_id}"
            )


crud_pdf_uploads = CRUDPdfUploads(PDFUpload)
