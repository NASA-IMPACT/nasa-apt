-- Revert nasa-apt:tables from pg

BEGIN;
DROP TABLE apt.atbd_versions CASCADE;
DROP TABLE apt.atbds CASCADE;
DROP TABLE apt.contact_groups CASCADE;
DROP TABLE apt.contacts CASCADE;
DROP TYPE apt.e_contact_role_type;
DROP TYPE apt.status;
DROP TYPE apt.contact_mechanism;
DROP TYPE apt.e_contact_mechanism_type;
COMMIT;
