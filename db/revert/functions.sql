-- Revert nasa-apt:functions from pg

BEGIN;
    DROP FUNCTION apt. create_atbd_version(
        IN "title" VARCHAR, 
        IN "created_by" VARCHAR, 
        IN "alias" VARCHAR,
        OUT "atbds.id",
        OUT "atbds.title",
        OUT "atbds.created_by",
        OUT "atbds.created_at",
        OUT "atbd_versions.id", 
        OUT "atbd_versions.major", 
        OUT "atbd_versions.minor",
        OUT "atbd_versions.status", 
        OUT "atbd_versions.document", 
        OUT "atbd_versions.published_by", 
        OUT "atbd_versions.published_at",
        OUT "atbd_versions.created_by",
        OUT "atbd_versions.created_at", 
        OUT "atbd_versions.changelog", 
        OUT "atbd_versions.doi"
    );
COMMIT;

