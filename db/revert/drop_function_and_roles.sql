-- Revert nasa-apt:drop_function_and_roles from pg
BEGIN;
-- XXX Add DDLs here.
CREATE ROLE anonymous noinherit;
GRANT anonymous TO masteruser;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA apt FROM anonymous;
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA apt FROM anonymous;
GRANT SELECT ON ALL TABLES IN SCHEMA apt TO anonymous;
GRANT USAGE ON SCHEMA apt TO anonymous;
ALTER TABLE apt.atbd_versions ENABLE ROW LEVEL SECURITY;
CREATE POLICY anon ON apt.atbd_versions TO anonymous USING (status = 'Published');
CREATE FUNCTION apt.create_atbd_version (title varchar, created_by varchar, alias varchar DEFAULT NULL,
-- Setting "atbds.id" INT failed when trying to return the expression
-- so I've set it to VARCHAR - which means I have have to cast the
-- of "atbds.id" from VARCHAR to INT when inserting into `atbd_versions`
OUT "atbds.id" int, OUT "atbds.title" varchar, OUT "atbds.alias" varchar, OUT "atbds.created_by" varchar, OUT "atbds.created_at" timestamptz, OUT "atbds.last_updated_by" varchar, OUT "atbds.last_updated_at" timestamptz, OUT "atbd_versions.atbd_id" int, OUT "atbd_versions.major" varchar, OUT "atbd_versions.minor" varchar, OUT "atbd_versions.status" apt.atbd_version_status, OUT "atbd_versions.document" json, OUT "atbd_versions.sections_completed" json, OUT "atbd_versions.published_by" varchar, OUT "atbd_versions.published_at" timestamptz, OUT "atbd_versions.created_by" varchar, OUT "atbd_versions.created_at" timestamptz, OUT "atbd_versions.last_updated_by" varchar, OUT "atbd_versions.last_updated_at" timestamptz, OUT "atbd_versions.changelog" varchar, OUT "atbd_versions.doi" varchar, OUT "atbd_versions.citation" json
)
AS $$
DECLARE
BEGIN
    INSERT INTO apt.atbds (title, created_by, last_updated_by, alias)
        VALUES (title, created_by, created_by, alias)
    RETURNING
        atbds.id, atbds.title, atbds.alias, atbds.created_by, atbds.created_at, atbds.last_updated_by, atbds.last_updated_at INTO "atbds.id", "atbds.title", "atbds.alias", "atbds.created_by", "atbds.created_at", "atbds.last_updated_by", "atbds.last_updated_at";
    INSERT INTO apt.atbd_versions (atbd_id, created_by, last_updated_by, major, minor)
        VALUES ("atbds.id", created_by, created_by, 1, 0)
    RETURNING
        atbd_versions.atbd_id, atbd_versions.major, atbd_versions.minor, atbd_versions.status, atbd_versions.document, atbd_versions.sections_completed, atbd_versions.published_by, atbd_versions.published_at, atbd_versions.created_by, atbd_versions.created_at, atbd_versions.last_updated_by, atbd_versions.last_updated_at, atbd_versions.changelog, atbd_versions.doi, atbd_versions.citation INTO "atbd_versions.atbd_id", "atbd_versions.major", "atbd_versions.minor", "atbd_versions.status", "atbd_versions.document", "atbd_versions.sections_completed", "atbd_versions.published_by", "atbd_versions.published_at", "atbd_versions.created_by", "atbd_versions.created_at", "atbd_versions.last_updated_by", "atbd_versions.last_updated_at", "atbd_versions.changelog", "atbd_versions.doi", "atbd_versions.citation";
END;
$$
LANGUAGE plpgsql
VOLATILE;
COMMIT;

