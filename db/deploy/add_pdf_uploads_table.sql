-- Deploy nasa-apt:add_pdf_uploads_table to pg
-- requires: threads_notify

BEGIN;

CREATE TABLE apt.pdf_uploads (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR NOT NULL,
    storage VARCHAR DEFAULT 's3',
    created_by VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atbd_id INTEGER NOT NULL,
    FOREIGN KEY (atbd_id) REFERENCES apt.atbds(id) ON DELETE CASCADE
);

COMMIT;
