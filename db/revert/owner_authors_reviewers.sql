-- Revert nasa-apt:owner_authors_reviewers from pg
BEGIN;
ALTER TABLE apt.atbd_versions
    DROP COLUMN "owner",
    DROP COLUMN authors,
    DROP COLUMN reviewers;
COMMIT;

