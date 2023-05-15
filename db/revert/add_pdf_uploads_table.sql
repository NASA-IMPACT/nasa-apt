-- Revert nasa-apt:add_pdf_uploads_table from pg

BEGIN;
DROP TABLE apt.pdf_uploads;
COMMIT;
