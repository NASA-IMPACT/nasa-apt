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
CREATE TYPE atbd_status AS ENUM (
  'Draft',
  'Published'
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
  historical_perspective VARCHAR (1024),
  status atbd_status default 'Draft'
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
CREATE FUNCTION create_atbd_version(OUT created_atbd atbds, OUT created_version atbd_versions)
  AS $$
  DECLARE
  BEGIN
  INSERT INTO atbds(title) VALUES ('') RETURNING * INTO created_atbd;
  INSERT INTO atbd_versions(atbd_id, atbd_version)
  VALUES (created_atbd.atbd_id, 1) RETURNING * INTO created_version;
  END;
  $$ LANGUAGE plpgsql
  VOLATILE;

INSERT INTO contacts(first_name, last_name, contact_mechanism_value)
VALUES ('Leonardo', 'Davinci', 'ld@gmail.comn');
INSERT INTO contacts(first_name, last_name, contact_mechanism_value)
VALUES ('Gregor', 'Mendel', 'genes@gmail.comn');
INSERT INTO atbds(title)
VALUES ('Test ATBD 1');
INSERT INTO atbd_contacts(atbd_id, contact_id)
VALUES (1, 1);
INSERT INTO atbd_versions(atbd_id, atbd_version, scientific_theory, introduction, historical_perspective)
VALUES (1, 1, 
'{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"A line of text in a paragraph."}]}]},
{"object":"block","type":"equation","nodes":[{"object":"text","leaves":[{"text":"\\int_0^\\infty x^2 dx"}]}]},
{"object":"block","type":"image","data":{"src":"http://localhost:4572/figures/fullmoon.jpg"}}]}}',
'Introduction Lorem Ipsum Text', 'Historical Perspective Lorem Ipsum Text');
INSERT INTO algorithm_input_variables(atbd_id, atbd_version, name, long_name)
VALUES (1, 1, 'Input Var 1', 'Input variable 1');
INSERT INTO algorithm_output_variables(atbd_id, atbd_version, name, long_name)
VALUES (1, 1, 'Output Var 1', 'Output variable 1');

