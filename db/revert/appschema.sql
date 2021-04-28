-- Revert nasa-apt:appschema from pg

BEGIN;
DROP SCHEMA apt CASCADE;
DROP OWNED by app_user;
DROP ROLE app_user;
COMMIT;
