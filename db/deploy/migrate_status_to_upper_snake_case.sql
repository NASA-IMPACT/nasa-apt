-- Deploy nasa-apt:migrate_status_to_upper_snake_case to pg
-- requires: tables
BEGIN;
-- XXX Add DDLs here.
ALTER TABLE apt.atbd_versions
    ADD COLUMN status_bkp varchar(1024);
UPDATE
    apt.atbd_versions
SET
    status_bkp = status;
ALTER TABLE apt.atbd_versions
    DROP COLUMN status;
DROP TYPE apt.atbd_version_status;
CREATE TYPE apt.atbd_version_status AS ENUM (
    'DRAFT',
    'CLOSED_REVIEW_REQUESTED',
    'CLOSED_REVIEW',
    'OPEN_REVIEW',
    'PUBLICATION_REQUESTED',
    'PUBLICATION',
    'PUBLISHED'
);
ALTER TABLE apt.atbd_versions
    ADD COLUMN "status" apt.atbd_version_status;
UPDATE
    apt.atbd_versions
SET
    "status" = 'PUBLISHED'
WHERE
    status_bkp = 'Published';
UPDATE
    apt.atbd_versions
SET
    "status" = 'DRAFT'
WHERE
    "status" IS NULL;
ALTER TABLE apt.atbd_versions
    ALTER COLUMN status SET DEFAULT 'DRAFT';
ALTER TABLE apt.atbd_versions
    DROP COLUMN status_bkp;
COMMIT;

