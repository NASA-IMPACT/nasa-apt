-- Deploy nasa-apt:owner_authors_reviewers to pg
-- requires: tables
BEGIN;
-- Add 3 new columns, all as nullable
ALTER TABLE apt.atbd_versions
    ADD COLUMN "owner" VARCHAR(1024),
    ADD COLUMN authors VARCHAR[],
    -- Reviewers will be a jsonb field with format
    -- { <cognito_sub> : "in_progress | done" }
    ADD COLUMN reviewers jsonb[];
-- Update `owner` column to match what is currently in the
-- `created_by` column
UPDATE
    apt.atbd_versions
SET
    "owner" = created_by;
-- Now that the `owner` column has been filled,
-- it can safely be set to non-null
ALTER TABLE apt.atbd_versions
    ALTER COLUMN "owner" SET NOT NULL;
COMMIT;

