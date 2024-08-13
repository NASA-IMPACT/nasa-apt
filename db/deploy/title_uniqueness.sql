-- Deploy nasa-apt:title_uniqueness to pg
-- requires: remove_reviewer_info_in_atbd_version

BEGIN;

ALTER TABLE apt.atbds ADD CONSTRAINT unique_title UNIQUE (title);

COMMIT;
