-- Revert nasa-apt:threads from pg
BEGIN;
DROP TYPE apt.thread_status;
DROP TYPE apt.document_section;
DROP TABLE apt.comments;
DROP TABLE apt.threads;
COMMIT;

