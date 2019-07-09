-- Deploy nasa-apt:tables to pg
-- requires: appschema

BEGIN;
CREATE TYPE apt.e_contact_mechanism_type AS ENUM (
 'Direct line',
 'Email',
 'Facebook',
 'Fax',
 'Mobile',
 'Modem',
 'Primary',
 'TDD/TTY phone',
 'Telephone',
 'Twitter',
 'U.S.',
 'Other'
);
CREATE TYPE apt.contact_mechanism AS (
 mechanism_type e_contact_mechanism_type,
 mechanism_value VARCHAR (1024)
);
CREATE TYPE apt.atbd_status AS ENUM (
  'Draft',
  'Published'
);
CREATE TYPE apt.e_contact_role_type AS ENUM (
 'Data center contact',
 'Technical contact',
 'Science contact',
 'Investigator',
 'Metadata author',
 'User services',
 'Science software development'
);
CREATE TABLE apt.contacts(
 contact_id serial PRIMARY KEY,
 first_name VARCHAR (1024) NOT NULL,
 middle_name VARCHAR (1024),
 last_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 url VARCHAR (1024),
 mechanisms contact_mechanism[],
 roles e_contact_role_type[]
);
CREATE TABLE apt.contact_groups(
 contact_group_id serial PRIMARY KEY,
 group_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 url VARCHAR (1024),
 mechanisms contact_mechanism[],
 roles e_contact_role_type[]
);
CREATE TABLE apt.atbds(
  atbd_id serial PRIMARY KEY,
  title VARCHAR (1024)
);
CREATE TABLE apt.atbd_contacts(
  atbd_id INTEGER NOT NULL,
  contact_id INTEGER NOT NULL,
  PRIMARY KEY (atbd_id, contact_id),
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
);
CREATE TABLE apt.atbd_contact_groups(
  atbd_id INTEGER NOT NULL,
  contact_group_id INTEGER NOT NULL,
  PRIMARY KEY (atbd_id, contact_group_id),
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  FOREIGN KEY (contact_group_id) REFERENCES contact_groups(contact_group_id)
);
CREATE TABLE apt.atbd_versions(
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  PRIMARY KEY (atbd_id, atbd_version),
  scientific_theory json,
  scientific_theory_assumptions json,
  mathematical_theory json,
  mathematical_theory_assumptions json,
  introduction json,
  historical_perspective json,
  performance_assessment_validation_methods json,
  performance_assessment_validation_uncertainties json,
  performance_assessment_validation_errors json,
  algorithm_usage_constraints json,
  status atbd_status default 'Draft'
);
CREATE TABLE apt.citations(
  citation_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  creators VARCHAR (1024),
  editors VARCHAR (1024),
  title VARCHAR (1024),
  series_name VARCHAR (1024),
  release_date VARCHAR (1024),
  release_place VARCHAR (1024),
  publisher VARCHAR (1024),
  version VARCHAR (1024),
  issue VARCHAR (1024),
  additional_details VARCHAR (1024),
  online_resource VARCHAR (1024)
);
CREATE TABLE apt.algorithm_input_variables(
  algorithm_input_variable_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  name VARCHAR (1024),
  long_name VARCHAR (1024),
  unit VARCHAR (1024)
);
CREATE TABLE apt.algorithm_output_variables(
  algorithm_output_variable_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  name VARCHAR (1024),
  long_name VARCHAR (1024),
  unit VARCHAR (1024)
);
CREATE TABLE apt.algorithm_implementations(
  algorithm_implementation_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  execution_description json NOT NULL
);
CREATE TABLE apt.publication_references(
  publication_reference_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  authors VARCHAR (1024),
  publication_date DATE,
  title VARCHAR (1024),
  series VARCHAR (1024),
  edition VARCHAR (1024),
  volume VARCHAR (1024),
  issue VARCHAR (1024),
  report_number VARCHAR (1024),
  publication_place VARCHAR (1024),
  publisher VARCHAR (1024),
  pages VARCHAR (1024),
  isbn VARCHAR (1024),
  doi VARCHAR (1024),
  online_resource VARCHAR (1024),
  other_reference_details VARCHAR (1024)
);
CREATE TABLE apt.data_access_input_data(
  data_access_input_data_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  description json
);
CREATE TABLE apt.data_access_output_data(
  data_access_output_data_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  description json
);
CREATE TABLE apt.data_access_related_urls(
  data_access_related_url_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  url VARCHAR (1024),
  description json
);
COMMIT;
