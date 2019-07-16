-- Revert nasa-apt:tables from pg

BEGIN;
DROP TABLE apt.data_access_related_urls CASCADE;
DROP TABLE apt.data_access_output_data CASCADE;
DROP TABLE apt.data_access_input_data CASCADE;
DROP TABLE apt.publication_references CASCADE;
DROP TABLE apt.algorithm_implementations CASCADE;
DROP TABLE apt.algorithm_output_variables CASCADE;
DROP TABLE apt.algorithm_input_variables CASCADE;
DROP TABLE apt.citations CASCADE;
DROP TABLE apt.atbd_versions CASCADE;
DROP TABLE apt.atbd_contact_groups CASCADE;
DROP TABLE apt.atbd_contacts CASCADE;
DROP TABLE apt.atbds CASCADE;
DROP TABLE apt.contact_groups CASCADE;
DROP TABLE apt.contacts CASCADE;
DROP TYPE apt.e_contact_role_type;
DROP TYPE apt.atbd_status;
DROP TYPE apt.contact_mechanism;
DROP TYPE apt.e_contact_mechanism_type;
COMMIT;
