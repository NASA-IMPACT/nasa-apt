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
CREATE TABLE atbds(
  atbd_id serial PRIMARY KEY,
  title VARCHAR (1024)
);
CREATE TABLE atbd_versions(
  atbd_version INTEGER NOT NULL,
  atbd_id INTEGER NOT NULL,
  FOREIGN KEY (atbd_id) REFERENCES atbds(atbd_id),
  PRIMARY KEY (atbd_id, atbd_version)
);
CREATE TABLE algorithm_descriptions(
  algorithm_description_id serial PRIMARY KEY,
  atbd_id INTEGER NOT NULL,
  atbd_version INTEGER NOT NULL,
  scientific_theory json,
  scientific_theory_assumptions json,
  mathematical_theory json,
  mathematical_theory_assumptions json,
  FOREIGN KEY (atbd_id, atbd_version) REFERENCES atbd_versions(atbd_id, atbd_version) ON DELETE CASCADE
);
CREATE TABLE algorithm_input_variables(
  algorithm_input_variable_id serial PRIMARY KEY,
  algorithm_description_id INTEGER,
  name VARCHAR (1024),
  long_name VARCHAR (1024),
  unit VARCHAR (1024),
  FOREIGN KEY (algorithm_description_id) REFERENCES algorithm_descriptions(algorithm_description_id) ON DELETE CASCADE
);

