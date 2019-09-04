-- Deploy nasa-apt:textsearch to pg
-- requires: atbdConstraint
-- requires: tables

BEGIN;
CREATE FUNCTION apt.search_text(searchstring text) returns SETOF apt.atbds
  LANGUAGE sql
  IMMUTABLE
  AS $_$
  SELECT
    apt.atbds.atbd_id,
    apt.atbds.title
  FROM apt.atbds
  INNER JOIN apt.atbd_contacts ON apt.atbd_contacts.atbd_id = apt.atbds.atbd_id
  INNER JOIN apt.contacts ON apt.contacts.contact_id = apt.atbd_contacts.contact_id
  WHERE to_tsvector(apt.contacts.first_name) @@ to_tsquery(searchstring);
  $_$;
COMMIT;
