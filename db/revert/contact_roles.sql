-- Revert nasa-apt:contact_roles from pg

BEGIN;
ALTER TABLE apt.atbd_versions_contacts
    DROP COLUMN roles;
DROP TYPE apt.e_contact_role_type;

CREATE TYPE apt.e_contact_role_type AS ENUM (
  'Data center contact',
  'Technical contact',
  'Science contact',
  'Investigator',
  'Metadata author',
  'User services',
  'Science software development'
);
ALTER TABLE apt.atbd_versions_contacts
    ADD COLUMN "roles" apt.e_contact_role_type[];
COMMIT;
