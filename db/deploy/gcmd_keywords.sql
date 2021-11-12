-- Deploy nasa-apt:gcmd_keywords to pg
-- requires: tables
BEGIN;
ALTER TABLE apt.atbd_versions
    ADD COLUMN "keywords" jsonb[] DEFAULT '{}';
COMMIT;

