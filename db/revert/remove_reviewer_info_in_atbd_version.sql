-- Revert nasa-apt:remove_reviewer_info_in_atbd_version from pg

BEGIN;

ALTER TABLE apt.atbd_versions
    ADD COLUMN "reviewer_info" json DEFAULT '{}';

COMMIT;
