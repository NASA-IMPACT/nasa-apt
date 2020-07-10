-- Deploy nasa-apt:atbdAlias to pg
-- requires: tables

BEGIN;
  alter TABLE apt.atbds
  add COLUMN alias VARCHAR(256) UNIQUE CONSTRAINT alphanum_alias CHECK(alias ~ '^[a-z0-9-]+$');
COMMIT;
