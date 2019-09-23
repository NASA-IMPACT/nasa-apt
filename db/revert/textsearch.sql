-- Revert nasa-apt:textsearch from pg
BEGIN;
DROP FUNCTION apt.search_text(searchstring text, statusstring text);
DROP TYPE apt.atbd_reduced;
DROP TYPE apt.atbd_reduced_versions;
COMMIT;

