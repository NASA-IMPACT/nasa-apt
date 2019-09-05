-- Revert nasa-apt:textsearch from pg
BEGIN;
DROP FUNCTION apt.search_text(searchstring text);
COMMIT;

