-- Deploy nasa-apt:threads_notify to pg
-- requires: threads

BEGIN;

ALTER TABLE apt.threads
    ADD COLUMN "notify" text[];

COMMIT;
