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
  mechanism_value varchar ( 1024));
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
CREATE TABLE apt.contacts (
  id serial PRIMARY KEY,
  first_name varchar(1024) NOT NULL,
  middle_name varchar(1024),
  last_name varchar(1024) NOT NULL,
  uuid varchar(1024),
  url varchar(1024),
  mechanisms apt.contact_mechanism[]
);
CREATE TABLE apt.atbds (
  id serial PRIMARY KEY,
  title varchar(1024) NOT NULL,
  alias varchar(256) UNIQUE CONSTRAINT alphanum_alias CHECK (alias ~ '^[a-z0-9-]+$') DEFAULT NULL,
  created_by varchar(1024) NOT NULL,
  created_at timestamptz DEFAULT now(),
  last_updated_by varchar(1024),
  last_updated_at timestamptz DEFAULT now()
);
-- Having only major (and not minor) included in the primary key
-- strictly enforces the fact that all minor version updates get "squashed" and
-- that APT only maintains major versions
CREATE TABLE apt.atbd_versions (
  major integer NOT NULL DEFAULT 1,
  minor integer NOT NULL DEFAULT 0,
  atbd_id integer NOT NULL,
  FOREIGN KEY (atbd_id) REFERENCES apt.atbds (id) ON DELETE CASCADE,
  PRIMARY KEY (atbd_id, major),
  "status" apt.atbd_version_status DEFAULT 'Draft',
  document json DEFAULT '{}',
  sections_completed json DEFAULT '{}',
  published_by varchar(1024),
  published_at timestamptz,
  created_by varchar(1024),
  created_at timestamptz DEFAULT now(),
  last_updated_by varchar(1024),
  last_updated_at timestamptz DEFAULT now(),
  changelog varchar,
  doi varchar(1024),
  citation json DEFAULT '{}'
);
CREATE TABLE apt.atbd_versions_contacts (
  atbd_id integer NOT NULL,
  major integer NOT NULL,
  FOREIGN KEY (atbd_id, major) REFERENCES apt.atbd_versions (atbd_id, major) ON DELETE CASCADE,
  contact_id integer NOT NULL,
  FOREIGN KEY (contact_id) REFERENCES apt.contacts (id) ON DELETE CASCADE,
  PRIMARY KEY (atbd_id, major, contact_id),
  roles apt.e_contact_role_type[]
);
COMMIT;

