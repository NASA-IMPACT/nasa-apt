-- Deploy nasa-apt:journal_status to pg
BEGIN;
CREATE TYPE apt.atbd_version_journal_status AS ENUM (
    'NO_PUBLICATION',
    'PUBLICATION_INTENDED',
    'PUBLICATION_REQUESTED',
    'PUBLISHED'
);
ALTER TABLE apt.atbd_versions
    ADD COLUMN journal_status apt.atbd_version_journal_status DEFAULT 'NO_PUBLICATION';
COMMIT;

