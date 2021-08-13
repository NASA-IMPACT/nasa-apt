-- Revert nasa-apt:threads from pg
BEGIN;
DROP TABLE apt.comments;
DROP TABLE apt.threads;
DROP TYPE apt.thread_status;
COMMIT;

