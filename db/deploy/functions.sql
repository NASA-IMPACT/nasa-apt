-- Deploy nasa-apt:functions to pg
-- requires: tables

BEGIN;
    CREATE FUNCTION apt.create_atbd_version( 
        title VARCHAR, 
        created_by VARCHAR,
        alias VARCHAR DEFAULT null,
        OUT created_atbd apt.atbds, 
        OUT created_version apt.atbd_versions)
  AS $$
    DECLARE
    BEGIN
        INSERT INTO apt.atbds
            (title, created_by, alias)
        VALUES
            (title, created_by, alias)
        RETURNING * INTO created_atbd;
    INSERT INTO apt.atbd_versions
        (atbd_id, id)
    VALUES
        (created_atbd.id, 1)
    RETURNING * INTO created_version;
END;
  $$ LANGUAGE plpgsql
  VOLATILE;
COMMIT;
