-- Deploy nasa-apt:add_pdf_in_atbd to pg
-- requires: add_pdf_uploads_table

BEGIN;

ALTER TABLE apt.atbd_versions
    ADD COLUMN "reviewer_info" json DEFAULT '{}';

COMMIT;
