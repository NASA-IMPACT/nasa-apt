-- Revert nasa-apt:corresponding_author_role from pg
BEGIN;
UPDATE
    apt.atbd_versions
SET
    "status" = 'DRAFT'
WHERE
    "status" IS NULL;
ALTER TABLE apt.atbd_versions
    ALTER COLUMN status SET DEFAULT 'DRAFT';
ALTER TABLE apt.atbd_versions_contacts
    ADD COLUMN roles_bkp varchar(1024);
UPDATE
    apt.atbd_versions_contacts
SET
    roles_bkp = roles;
ALTER TABLE apt.atbd_versions_contacts
    DROP COLUMN roles;
DROP TYPE apt.e_contact_role_type;
CREATE TYPE apt.e_contact_role_type AS ENUM (
    'Writing – original draft',
    'Writing – review & editing',
    'Validation',
    'Data curation',
    'Conceptualization',
    'Methodology',
    'Visualization',
    'Formal analysis',
    'Software',
    'Resources',
    'Project administration',
    'Supervision',
    'Investigation',
    'Funding acquisition'
);
ALTER TABLE apt.atbd_versions_contacts
    ADD COLUMN "roles" apt.e_contact_role_type[] DEFAULT '{}';
UPDATE
    apt.atbd_versions_contacts
SET
    "roles" = "roles_bkp"::apt.e_contact_role_type[]
WHERE
    roles_bkp != 'Corresponding Author';
ALTER TABLE apt.atbd_versions_contacts
    DROP COLUMN roles_bkp;
COMMIT;

