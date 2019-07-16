-- Verify nasa-apt:tables on pg

BEGIN;
  SELECT contact_id
    FROM apt.contacts
  WHERE FALSE;
ROLLBACK;
