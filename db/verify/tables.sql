-- Verify nasa-apt:tables on pg

BEGIN;
    SELECT id
    FROM apt.contacts
    WHERE FALSE;
    ROLLBACK;
