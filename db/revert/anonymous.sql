-- Revert nasa-apt:anonymous from pg

BEGIN;

    -- XXX Add DDLs here.
    DROP OWNED BY anonymous;
    DROP ROLE anonymous;
COMMIT;
