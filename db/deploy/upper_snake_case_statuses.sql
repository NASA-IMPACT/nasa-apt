-- Deploy nasa-apt:upper_snake_case_statuses to pg
BEGIN;
ALTER TYPE apt.atbd_version_status RENAME ATTRIBUTE "Draft" TO "DRAFT" CASCADE;
ALTER TYPE apt.atbd_version_status RENAME ATTRIBUTE "Reivew" TO "REVIEW" CASCADE;
ALTER TYPE apt.atbd_version_status RENAME ATTRIBUTE "Published" TO "PUBLISHED" CASCADE;
UPDATE
    apt.abtd_versions
SET
    "status" = 'DRAFT'
WHERE
    "status" == 'Draft';
UPDATE
    apt.abtd_versions
SET
    "status" = 'DRAFT'
WHERE
    "status" == 'Review';
UPDATE
    apt.abtd_versions
SET
    "status" = 'PUBLISHED'
WHERE
    "status" == 'Published';
COMMIT;

