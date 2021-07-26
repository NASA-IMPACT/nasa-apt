-- Revert nasa-apt:journal_status from pg
BEGIN;
ALTER TABLE apt.atbd_versions
    DROP COLUMN journal_status;
DROP TYPE apt.atbd_version_journal_status;
COMMIT;

