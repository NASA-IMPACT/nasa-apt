-- Deploy nasa-apt:publication_checklist to pg
-- requires: tables

BEGIN;
ALTER TABLE apt.atbd_versions
  ADD COLUMN publication_checklist json DEFAULT '{"journal_editor": "Chelle Gentemann"}';

UPDATE
  apt.atbd_versions
SET
  publication_checklist = '{
    "journal_editor": "Chelle Gentemann"
  }'::jsonb;
COMMIT;
