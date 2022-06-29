-- Revert nasa-apt:version_lock from pg

BEGIN;

ALTER TABLE apt.atbd_versions
    DROP COLUMN "locked_by";

COMMIT;
