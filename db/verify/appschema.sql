-- Verify nasa-apt:appschema on pg

BEGIN;
SELECT pg_catalog.has_schema_privilege('apt', 'usage');
ROLLBACK;
