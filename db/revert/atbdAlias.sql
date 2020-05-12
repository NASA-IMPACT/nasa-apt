-- Revert nasa-apt:atbdAlias from pg

BEGIN;
  alter TABLE apt.atbds
  drop COLUMN alias;
COMMIT;
