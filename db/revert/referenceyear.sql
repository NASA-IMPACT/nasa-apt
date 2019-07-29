-- Revert nasa-apt:referenceyear from pg

BEGIN;
  alter TABLE apt.publication_references
  drop COLUMN year;
COMMIT;
