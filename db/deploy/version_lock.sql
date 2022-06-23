-- Deploy nasa-apt:version_lock to pg
-- requires: tables

BEGIN;

ALTER TABLE apt.atbd_versions
    ADD COLUMN "locked_by" VARCHAR(1024);

COMMIT;
