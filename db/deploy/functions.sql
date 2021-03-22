-- Deploy nasa-apt:functions to pg
-- requires: tables

BEGIN;
    CREATE FUNCTION apt.create_atbd_version( 
        title VARCHAR,
        created_by VARCHAR,
        alias VARCHAR DEFAULT NULL,
        -- Setting "atbds.id" INT failed when trying to return the expression
        -- so I've set it to VARCHAR - which means I have have to cast the 
        -- of "atbds.id" from VARCHAR to INT when inserting into `atbd_versions`
        OUT "atbds.id" INT,
        OUT "atbds.title" VARCHAR,
        OUT "atbds.alias" VARCHAR,
        OUT "atbds.created_by" VARCHAR,
        OUT "atbds.created_at" TIMESTAMPTZ,
        OUT "atbd_versions.atbd_id" INT, 
        OUT "atbd_versions.major" VARCHAR, 
        OUT "atbd_versions.minor" VARCHAR,
        OUT "atbd_versions.status" apt.atbd_version_status, 
        OUT "atbd_versions.document" JSON, 
        OUT "atbd_versions.sections_completed" JSON, 
        OUT "atbd_versions.published_by" VARCHAR, 
        OUT "atbd_versions.published_at" TIMESTAMPTZ,
        OUT "atbd_versions.created_by" VARCHAR,
        OUT "atbd_versions.created_at" TIMESTAMPTZ,
        OUT "atbd_versions.changelog" VARCHAR,
        OUT "atbd_versions.doi" VARCHAR
        )
  AS $$
    DECLARE
    BEGIN
        INSERT INTO apt.atbds
            (title, created_by, alias)
        VALUES
            (title, created_by, alias)
        RETURNING atbds.id, atbds.title, atbds.alias, atbds.created_by, atbds.created_at
        INTO "atbds.id", "atbds.title", "atbds.alias", "atbds.created_by", "atbds.created_at";
        
        INSERT INTO apt.atbd_versions
            (atbd_id, created_by, major, minor)
        VALUES
            ("atbds.id", created_by, 1, 0)
        RETURNING atbd_versions.atbd_id, atbd_versions.major, atbd_versions.minor, atbd_versions.status, atbd_versions.document, atbd_versions.sections_completed, atbd_versions.published_by, atbd_versions.published_at, atbd_versions.created_by, atbd_versions.created_at, atbd_versions.changelog, atbd_versions.doi 
        INTO "atbd_versions.atbd_id", "atbd_versions.major", "atbd_versions.minor", "atbd_versions.status", "atbd_versions.document", "atbd_versions.sections_completed", "atbd_versions.published_by", "atbd_versions.published_at", "atbd_versions.created_by", "atbd_versions.created_at", "atbd_versions.changelog", "atbd_versions.doi";
    END;
    $$ LANGUAGE plpgsql
  VOLATILE;
COMMIT;

 