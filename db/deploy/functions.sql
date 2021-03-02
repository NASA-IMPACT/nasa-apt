-- Deploy nasa-apt:functions to pg
-- requires: tables

BEGIN;
    CREATE FUNCTION apt.create_atbd_version( 
        title VARCHAR, 
        created_by VARCHAR,
        alias VARCHAR DEFAULT NULL,
        -- OUT created_atbd apt.atbds, 
        -- OUT created_version apt.atbd_versions)
        OUT "atbds.id" INT,
        OUT "atbds.title" VARCHAR,
        OUT "atbds.created_by" VARCHAR,
        OUT "atbds.created_at" TIMESTAMPTZ,
        OUT "atbd_versions.id" INT, 
        OUT "atbd_versions.atbd_id" VARCHAR, 
        OUT "atbd_versions.alias" VARCHAR, 
        OUT "atbd_versions.status" apt.atbd_version_status, 
        OUT "atbd_versions.document" VARCHAR, 
        OUT "atbd_versions.published_by" VARCHAR, 
        OUT "atbd_versions.published_at" TIMESTAMPTZ)
  AS $$
    DECLARE
    BEGIN
        INSERT INTO apt.atbds
            (title, created_by, alias)
        VALUES
            (title, created_by, alias)
        RETURNING atbds.id, atbds.title, atbds.created_by, atbds.created_at INTO "atbds.id", "atbds.title", "atbds.created_by", "atbds.created_at";
        -- RETURNING * INTO created_atbd;
        
        INSERT INTO apt.atbd_versions
            (atbd_id, id)
        VALUES
            ("atbds.id", 1)
            -- (created_atbd.id, 1)
        RETURNING atbd_versions.atbd_id, atbd_versions.id, atbd_versions.alias, atbd_versions.status, atbd_versions.document, atbd_versions.published_by, atbd_versions.published_at INTO "atbd_versions.id", "atbd_versions.atbd_id", "atbd_versions.alias", "atbd_versions.status", "atbd_versions.document", "atbd_versions.published_by", "atbd_versions.published_at";
        -- RETURNING * INTO created_version;
    END;
    $$ LANGUAGE plpgsql
  VOLATILE;
COMMIT;

 