-- Revert nasa-apt:functions from pg

BEGIN;
    DROP FUNCTION apt.create_atbd_version
    (OUT created_atbd apt.atbds, OUT created_version apt.atbd_versions);
COMMIT;
