-- Deploy nasa-apt:atbdConstraint to pg
-- requires: tables

BEGIN;
  alter TABLE apt.atbd_versions
  drop CONSTRAINT atbd_versions_atbd_id_fkey;

  alter TABLE apt.atbd_versions
  add constraint atbd_id
  FOREIGN KEY (atbd_id) REFERENCES apt.atbds(atbd_id)
  ON DELETE CASCADE;
COMMIT;
