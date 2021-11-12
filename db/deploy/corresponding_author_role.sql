-- Deploy nasa-apt:corresponding_author_role to pg
-- requires: contact_roles
BEGIN;
ALTER TYPE apt.e_contact_role_type
    ADD VALUE 'Corresponding Author';
COMMIT;

