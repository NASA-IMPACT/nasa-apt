-- Deploy nasa-apt:threads to pg

BEGIN;

CREATE TABLE apt.threads (
    id serial PRIMARY KEY,
    atbd_id integer NOT NULL,
    major integer NOT NULL,
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
    comment TEXT
);

COMMIT;
