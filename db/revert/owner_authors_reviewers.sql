-- Revert nasa-apt:owner_authors_reviewers from pg
BEGIN;
ALTER TABLE apt.atbd_versions
    DROP COLUMN OWNER VARCHAR(1024),
    DROP COLUMN authors varchar[],
    DROP COLUMN reviewers varchar[]
COMMIT;

