-- Deploy nasa-apt:journalDetails to pg
-- requires: tables

BEGIN;
  ALTER TABLE apt.atbd_versions
    ADD COLUMN journal_discussion json,
    ADD COLUMN journal_acknowledgements json;
COMMIT;
