-- Revert nasa-apt:add_pdf_in_atbd from pg

BEGIN;


ALTER TABLE apt.atbds
    DROP COLUMN "document_type";

DROP TYPE apt.atbd_document_type;

ALTER TABLE apt.atbd_versions
    DROP COLUMN "pdf_id";

COMMIT;
