-- Deploy nasa-apt:referenceyear to pg
-- requires: tables

BEGIN;
  alter TABLE apt.publication_references
  add COLUMN year integer;
COMMIT;
