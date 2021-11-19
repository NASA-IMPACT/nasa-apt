-- Revert nasa-apt:contact_affiliations from pg
BEGIN;
ALTER TABLE apt.atbd_versions_contacts
    DROP COLUMN affiliations;
COMMIT;

