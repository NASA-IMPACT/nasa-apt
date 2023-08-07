-- Revert nasa-apt:add_reviewer_info_in_atbd_version from pg

BEGIN;

ALTER TABLE apt.atbd_versions
    DROP COLUMN "reviewer_info";

COMMIT;
