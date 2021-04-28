-- Revert nasa-apt:copyATBD from pg

BEGIN;

DROP FUNCTION apt.copy_atbd(originalid integer, OUT new_id integer, OUT created_atbd apt.atbds);
DROP EXTENSION hstore;

COMMIT;
