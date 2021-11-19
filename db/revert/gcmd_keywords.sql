-- Revert nasa-apt:gcmd_keywords from pg
BEGIN;
ALTER TABLE apt.atbd_versions
    DROP COLUMN keywords;
COMMIT;

