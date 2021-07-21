-- Revert nasa-apt:migrate_status_to_upper_snake_case from pg
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
    'Draft',
    'Review',
    'Published'
);
ALTER TABLE apt.atbd_versions
    ADD COLUMN "status" apt.atbd_version_status;
UPDATE
    apt.atbd_versions
SET
    "status" = 'Published'
WHERE
    status_bkp = 'PUBLISHED';
UPDATE
    apt.atbd_versions
SET
    "status" = 'Draft'
WHERE
    "status" IS NULL;
ALTER TABLE apt.atbd_versions
    ALTER COLUMN status SET DEFAULT 'Draft';
ALTER TABLE apt.atbd_versions
    DROP COLUMN status_bkp;
COMMIT;

