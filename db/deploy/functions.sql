-- Deploy nasa-apt:functions to pg
-- requires: tables

BEGIN;
CREATE FUNCTION apt.create_atbd_version(OUT created_atbd apt.atbds, OUT created_version apt.atbd_versions)
  AS $$
  DECLARE
  BEGIN
  INSERT INTO apt.atbds(title) VALUES ('') RETURNING * INTO created_atbd;
  INSERT INTO apt.atbd_versions(atbd_id, atbd_version)
  VALUES (created_atbd.atbd_id, 1) RETURNING * INTO created_version;
  END;
  $$ LANGUAGE plpgsql
  VOLATILE;
COMMIT;
