-- Revert nasa-apt:appschema from pg

BEGIN;
DROP SCHEMA apt;
DROP ROLE app_user;
COMMIT;
