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
 mechanism_type apt.e_contact_mechanism_type,
 mechanism_value VARCHAR (1024)
);
CREATE TYPE apt.atbd_version_status AS ENUM (
  'Draft',
  'Review',
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
 id serial PRIMARY KEY,
 first_name VARCHAR (1024) NOT NULL,
 middle_name VARCHAR (1024),
 last_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 url VARCHAR (1024),
 mechanisms apt.contact_mechanism[],
 roles apt.e_contact_role_type[]
);
CREATE TABLE apt.contact_groups(
 id serial PRIMARY KEY,
 group_name VARCHAR (1024) NOT NULL,
 uuid VARCHAR (1024),
 url VARCHAR (1024),
 mechanisms apt.contact_mechanism[],
 roles apt.e_contact_role_type[]
);
CREATE TABLE apt.atbds(
  id serial PRIMARY KEY,
  title VARCHAR (1024) NOT NULL,
  alias VARCHAR(256) UNIQUE CONSTRAINT alphanum_alias CHECK(alias ~ '^[a-z0-9-]+$'),
  created_by VARCHAR (1024),
  created_at TIMESTAMPTZ default now()
);
CREATE TABLE apt.atbd_versions(
    id INTEGER NOT NULL,
    atbd_id INTEGER NOT NULL,
    FOREIGN KEY (atbd_id) REFERENCES apt.atbds(id),
    PRIMARY KEY (atbd_id, id), 
    alias VARCHAR(256) CONSTRAINT alphanum_alias CHECK(alias ~ '^[.a-z0-9-]+$'),
    status apt.atbd_version_status default 'Draft',
    document json,
    published_by VARCHAR(1024),
    published_at TIMESTAMPTZ 
);
COMMIT;