-- Revert nasa-apt:title_uniqueness from pg

BEGIN;

ALTER TABLE apt.atbds DROP CONSTRAINT unique_title;

COMMIT;
