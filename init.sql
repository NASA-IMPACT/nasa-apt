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
  PRIMARY KEY (atbd_id, atbd_version),
  scientific_theory json,
  scientific_theory_assumptions json,
  mathematical_theory json,
  mathematical_theory_assumptions json
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
INSERT INTO atbds(title)
VALUES ('Test ATBD 1');
INSERT INTO atbd_versions(atbd_id, atbd_version, scientific_theory)
VALUES (1, 1, '{"document":{"nodes":[{"object":"block","type":"paragraph","nodes":[{"object":"text","leaves":[{"text":"A line of text in a paragraph."}]}]},{"object":"block","type":"equation","nodes":[{"object":"text","leaves":[{"text":"\\int_0^\\infty x^2 dx"}]}]},{"object":"block","type":"image","data":{"src":"https://img.washingtonpost.com/wp-apps/imrs.php?src=https://img.washingtonpost.com/news/speaking-of-science/wp-content/uploads/sites/36/2015/10/as12-49-7278-1024x1024.jpg&w=1484"}}]}}');
INSERT INTO algorithm_input_variables(atbd_id, atbd_version, name)
VALUES (1, 1, 'Input variable 1');
