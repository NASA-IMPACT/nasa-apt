-- Revert nasa-apt:threads_notify from pg

BEGIN;

ALTER TABLE apt.threads
    DROP COLUMN "notify";

COMMIT;
