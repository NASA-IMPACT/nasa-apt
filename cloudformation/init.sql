CREATE ROLE app_user;
GRANT app_user TO masteruser;
CREATE SCHEMA apt;
GRANT USAGE ON SCHEMA apt TO app_user;
GRANT CONNECT ON DATABASE nasadb TO app_user;
GRANT USAGE ON SCHEMA apt TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA apt TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA apt GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
SET SCHEMA 'apt';

CREATE TYPE e_contact_mechanism_type AS ENUM (
 'Direct Line', 
 'Email', 
 'Facebook',
 'Fax',
 'Mobile',
 'Modem',
 'Primary',
 'TDD/TTY Phone',
 'Telephone',
 'Twitter',
 'U.S.',
 'Other'
);
CREATE TABLE contacts(
 contact_id serial PRIMARY KEY,
 first_name VARCHAR (1024) NOT NULL,
 middle_name VARCHAR (1024),
 last_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 contact_mechanism_type e_contact_mechanism_type default 'Email',
 contact_mechanism_value VARCHAR (1024) NOT NULL
);
CREATE TABLE contact_groups(
 contact_group_id serial PRIMARY KEY,
 group_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 contact_mechanism_type e_contact_mechanism_type default 'Email',
 contact_mechanism_value VARCHAR (1024) NOT NULL
);
CREATE TABLE atbds(
  atbd_id serial PRIMARY KEY,
  title VARCHAR (1024)
);
CREATE TABLE atbd_contacts(
  atbd_id INTEGER NOT NULL,
  contact_id INTEGER NOT NULL,
  PRIMARY KEY (atbd_id, contact_id),
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  FOREIGN KEY (contact_id) REFERENCES contacts(contact_id)
);
CREATE TABLE atbd_contact_groups(
  atbd_id INTEGER NOT NULL,
  contact_group_id INTEGER NOT NULL,
  PRIMARY KEY (atbd_id, contact_group_id),
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  FOREIGN KEY (contact_group_id) REFERENCES contact_groups(contact_group_id)
);
CREATE TABLE atbd_versions(
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  PRIMARY KEY (atbd_id, atbd_version),
  scientific_theory json,
  scientific_theory_assumptions json,
  mathematical_theory json,
  mathematical_theory_assumptions json,
  introduction VARCHAR (1024),
  historical_perspective VARCHAR (1024)
);
CREATE TABLE algorithm_input_variables(
  algorithm_input_variable_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  name VARCHAR (1024),
  long_name VARCHAR (1024),
  unit VARCHAR (1024)
);
CREATE TABLE algorithm_output_variables(
  algorithm_output_variable_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  name VARCHAR (1024),
  long_name VARCHAR (1024),
  unit VARCHAR (1024)
);
CREATE TABLE algorithm_implementations(
  algorithm_implementation_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  execution_description json NOT NULL
);
CREATE TABLE performance_assessment_validation_methods(
  performance_assessment_validation_method_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  description json
);
CREATE TABLE performance_assessment_validation_uncertainties(
  performance_assessment_validation_uncertainty serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  description json
);
CREATE TABLE performance_assessment_validation_errors(
  performance_assessment_validation_error serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  description json
);
CREATE TABLE publication_references(
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
CREATE TABLE data_access_input_data(
  data_access_input_data_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  description VARCHAR (4000)
);
CREATE TABLE data_access_output_data(
  data_access_output_data_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  access_url VARCHAR (1024),
  description VARCHAR (4000)
);
CREATE TABLE data_access_related_urls(
  data_access_related_url_id serial PRIMARY KEY,
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE,
  url VARCHAR (1024),
  description VARCHAR (4000)
);