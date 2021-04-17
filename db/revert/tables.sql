-- Revert nasa-apt:tables from pg

BEGIN;
DROP TABE apt.atbd_versions_contacts;
DROP TABLE apt.atbd_versions CASCADE;
DROP TABLE apt.atbds CASCADE;
DROP TABLE apt.contacts CASCADE;
DROP TYPE apt.e_contact_role_type;
DROP TYPE apt.atbd_version_status;
DROP TYPE apt.contact_mechanism;
DROP TYPE apt.e_contact_mechanism_type;
COMMIT;
