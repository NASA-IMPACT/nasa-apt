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
 mechanisms apt.contact_mechanism []
);
CREATE TABLE apt.atbds(
  id serial PRIMARY KEY,
  title VARCHAR (1024) NOT NULL,
  alias VARCHAR(256) UNIQUE CONSTRAINT alphanum_alias CHECK(alias ~ '^[a-z0-9-]+$') DEFAULT NULL,
  created_by VARCHAR (1024) NOT NULL,
  created_at TIMESTAMPTZ default now(),
  last_updated_by VARCHAR(1024), 
  last_updated_at TIMESTAMPTZ default now()
);
-- Having only major (and not minor) included in the primary key
-- strictly enforces the fact that all minor version updates get "squashed" and 
-- that APT only maintains major versions
CREATE TABLE apt.atbd_versions(
    major INTEGER NOT NULL default 1,
    minor INTEGER NOT NULL default 0,
    atbd_id INTEGER NOT NULL,
    FOREIGN KEY (atbd_id) REFERENCES apt.atbds(id) ON DELETE CASCADE,
    PRIMARY KEY (atbd_id, major), 
    "status" apt.atbd_version_status default 'Draft',
    document json default '{}',
    sections_completed json default '{}',
    published_by VARCHAR(1024),
    published_at TIMESTAMPTZ,
    created_by VARCHAR(1024),
    created_at TIMESTAMPTZ default now(),
    last_updated_by VARCHAR(1024),
    last_updated_at TIMESTAMPTZ default now(),
    changelog VARCHAR,
    doi VARCHAR(1024),
    citation JSON default '{}'
);
CREATE TABLE apt.atbd_versions_contacts(
  atbd_id INTEGER NOT NULL,
  major INTEGER NOT NULL,
  FOREIGN KEY (atbd_id, major) REFERENCES apt.atbd_versions(atbd_id, major) ON DELETE CASCADE,
  contact_id INTEGER NOT NULL,
  FOREIGN KEY (contact_id) REFERENCES apt.contacts(id),
  roles apt.e_contact_role_type[] 
);
COMMIT;