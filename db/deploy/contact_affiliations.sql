-- Deploy nasa-apt:contact_affiliations to pg
-- requires: tables
BEGIN;
ALTER TABLE apt.atbd_versions_contacts
    ADD COLUMN "affiliations" text[] DEFAULT '{}';
COMMIT;

