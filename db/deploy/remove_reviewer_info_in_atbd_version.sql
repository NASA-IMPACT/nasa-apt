-- Deploy nasa-apt:remove_reviewer_info_in_atbd_version to pg
-- requires: add_reviewer_info_in_atbd_version

BEGIN;

-- NOTE: This will cause data loss
ALTER TABLE apt.atbd_versions
    DROP COLUMN "reviewer_info";

COMMIT;
