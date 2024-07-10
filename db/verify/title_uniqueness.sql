-- Verify nasa-apt:title_uniqueness on pg

SELECT conname
FROM pg_constraint
WHERE conname = 'unique_title' AND conrelid = 'apt.atbds'::regclass;
