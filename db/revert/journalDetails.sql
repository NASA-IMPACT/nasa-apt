-- Revert nasa-apt:journalDetails from pg

BEGIN;
  ALTER TABLE apt.atbds
    DROP COLUMN journal_discussion,
    DROP COLUMN journal_acknowledgements;
COMMIT;
