-- Revert nasa-apt:publication_checklist from pg

BEGIN;
ALTER TABLE apt.atbd_versions
    DROP COLUMN publication_checklist;
COMMIT;
