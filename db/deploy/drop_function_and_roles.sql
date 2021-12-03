-- Deploy nasa-apt:drop_function_and_roles to pg
-- requires: appschema
BEGIN;
-- XXX Add DDLs here.
ALTER TABLE apt.atbd_versions DISABLE ROW LEVEL SECURITY;
DROP POLICY anon ON apt.atbd_versions;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA apt FROM anonymous;
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA apt FROM anonymous;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA apt FROM anonymous;
REVOKE ALL PRIVILEGES ON SCHEMA apt FROM anonymous;
DROP ROLE anonymous;
DROP FUNCTION apt.create_atbd_version (IN "title" VARCHAR, IN "created_by" VARCHAR, IN "alias" VARCHAR, OUT "atbds.id", OUT "atbds.title", OUT "atbds.created_by", OUT "atbds.created_at", OUT "atbds.last_updated_by", OUT "atbds.last_updated_at", OUT "atbd_versions.id", OUT "atbd_versions.major", OUT "atbd_versions.minor", OUT "atbd_versions.status", OUT "atbd_versions.document", OUT "atbd_versions.sections_completed", OUT "atbd_versions.published_by", OUT "atbd_versions.published_at", OUT "atbd_versions.created_by", OUT "atbd_versions.created_at", OUT "atbd_versions.last_updated_by", OUT "atbd_versions.last_updated_at", OUT "atbd_versions.changelog", OUT "atbd_versions.doi", OUT "atbd_versions.citation");
COMMIT;

