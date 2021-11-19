-- Deploy nasa-apt:migrate_contact_roles_to_text_array to pg
-- requires: contact_roles
BEGIN;
-- NOTE we are not dropping the `e_contact_role_type` TYPE
-- because the `roles` column still depends on int
ALTER TABLE apt.atbd_versions_contacts
    ALTER COLUMN "roles" TYPE text[]
    USING roles::text[];
ALTER TABLE apt.atbd_versions_contacts
    ALTER COLUMN "roles" DROP DEFAULT;
ALTER TABLE apt.atbd_versions_contacts
    ALTER COLUMN "roles" SET DEFAULT '{}';
DROP TYPE apt.e_contact_role_type;
COMMIT;

