-- Deploy nasa-apt:contact_roles to pg
-- requires: tables

BEGIN;
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
COMMIT;
