-- Revert nasa-apt:tables from pg

BEGIN;
DROP TABLE apt.data_access_related_urls;
DROP TABLE apt.data_access_output_data;
DROP TABLE apt.data_access_input_data;
DROP TABLE apt.publication_references;
DROP TABLE apt.algorithm_implementations;
DROP TABLE apt.algorithm_output_variables;
DROP TABLE apt.algorithm_input_variables;
DROP TABLE apt.citations;
DROP TABLE apt.atbd_versions;
DROP TABLE apt.atbd_contact_groups;
DROP TABLE apt.atbd_contacts;
DROP TABLE apt.atbds;
DROP TABLE apt.contact_groups;
DROP TABLE apt.contacts;
DROP TYPE apt.e_contact_role_type;
DROP TYPE apt.atbd_status; 
DROP TYPE apt.contact_mechanism; 
DROP TYPE apt.e_contact_mechanism_type;
COMMIT;
