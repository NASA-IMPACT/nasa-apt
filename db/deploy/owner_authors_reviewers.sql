-- Deploy nasa-apt:owner_authors_reviewers to pg
-- requires: tables
BEGIN;
ALTER TABLE apt.atbd_versions
    ADD COLUMN "owner" VARCHAR(1024),
    ADD COLUMN authors varchar[],
    ADD COLUMN reviewers varchar[];
COMMIT;

BEGIN;
UPDATE
    TABLE apt.atbd_versions
SET
    "owner" = created_by;
COMMIT;

