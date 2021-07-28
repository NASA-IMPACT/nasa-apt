-- Revert nasa-apt:threads from pg

BEGIN;
DROP TABLE apt.comments;
DROP TABLE apt.threads;
COMMIT;
