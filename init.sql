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
