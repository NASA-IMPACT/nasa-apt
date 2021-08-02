-- Deploy nasa-apt:threads to pg

BEGIN;

CREATE TYPE apt.thread_status AS ENUM (
  'Open',
  'Closed'
);

CREATE TYPE apt.document_section AS ENUM (
  'general',
  'citation',
  'contacts',
  'introduction',
  'historical_perspective',
  'scientific_theory',
  'mathematical_theory',
  'input_variables',
  'output_variables',
  'constraints',
  'validation',
  'algorithm_implementations',
  'data_access_input_data',
  'data_access_output_data',
  'data_access_related_urls',
  'discussion',
  'acknowledgements'
);

CREATE TABLE apt.threads (
    id serial PRIMARY KEY,
    atbd_id integer NOT NULL,
    major integer NOT NULL,
    "status" apt.thread_status DEFAULT 'Open',
    "section" apt.document_section NOT NULL, 
    FOREIGN KEY (atbd_id, major) REFERENCES apt.atbd_versions (atbd_id, major) ON DELETE CASCADE
);

CREATE TABLE apt.comments (
    id serial PRIMARY KEY,
    thread_id serial NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES apt.threads (id) ON DELETE CASCADE,
    created_by VARCHAR(1024),
    created_at timestamptz DEFAULT now(),
    last_updated_by varchar(1024),
    last_updated_at timestamptz DEFAULT now(),
    body TEXT
);

COMMIT;
