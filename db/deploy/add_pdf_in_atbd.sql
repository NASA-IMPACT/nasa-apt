-- Deploy nasa-apt:add_pdf_in_atbd to pg
-- requires: add_pdf_uploads_table

BEGIN;

CREATE TYPE apt.atbd_document_type AS ENUM (
  'HTML',
  'PDF'
);

ALTER TABLE apt.atbds
    ADD COLUMN "document_type" apt.atbd_document_type DEFAULT 'HTML';

ALTER TABLE apt.atbd_versions
    ADD COLUMN "pdf_id" integer,
    ADD CONSTRAINT fk_pdf_id FOREIGN KEY (pdf_id) REFERENCES apt.pdf_uploads (id) ON DELETE CASCADE;

COMMIT;
