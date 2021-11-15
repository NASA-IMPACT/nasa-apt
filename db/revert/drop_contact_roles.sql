-- Revert nasa-apt:migrate_contact_roles_to_text_array from pg
BEGIN;
-- Reverts
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
    ALTER COLUMN "roles" TYPE apt.e_contact_role_type[]
    USING roles::apt.e_contact_role_type[];
ALTER TABLE apt.atbd_versions_contacts
    ALTER COLUMN "roles" DROP DEFAULT;
ALTER TABLE apt.atbd_versions_contacts
    ALTER COLUMN "roles" SET DEFAULT '{}';
COMMIT;

