-- Deploy nasa-apt:journal_status to pg
BEGIN;
CREATE TYPE apt.atbd_version_journal_status AS ENUM (
    'PUBLICATION_REQUESTED',
    'PUBLICATION_INTENDED',
    'PUBLISHED'
);
ALTER TABLE apt.atbd_versions
    ADD COLUMN journal_status apt.atbd_version_journal_status;
COMMIT;

