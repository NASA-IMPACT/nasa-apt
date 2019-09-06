-- Deploy nasa-apt:textsearch to pg
-- requires: atbdConstraint
-- requires: tables

--  BEGIN;
--  CREATE FUNCTION apt.search_text(searchstring text) returns SETOF apt.atbds
  --  LANGUAGE sql
  --  IMMUTABLE
  --  AS $_$
  --  SELECT DISTINCT
    --  apt.atbds.atbd_id,
    --  apt.atbds.title
  --  FROM apt.atbds
  --  LEFT OUTER JOIN apt.atbd_contacts ON apt.atbd_contacts.atbd_id = apt.atbds.atbd_id
  --  LEFT OUTER JOIN apt.contacts ON apt.contacts.contact_id = apt.atbd_contacts.contact_id
  --  WHERE to_tsvector(CONCAT(apt.contacts.first_name, ' ', apt.contacts.last_name)) @@ to_tsquery(searchstring)
  --  OR to_tsvector(apt.atbds.title) @@ to_tsquery(searchstring);
  --  $_$;
--  COMMIT;
BEGIN;
CREATE TYPE apt.atbd_reduced_version AS (
  atbd_id INTEGER,
  atbd_version INTEGER,
  status apt.atbd_status
);
CREATE TYPE apt.atbd_reduced AS (
  atbd_id INTEGER,
  title VARCHAR (1024),
  contacts apt.contacts[]
);

CREATE FUNCTION apt.search_text(searchstring text) returns SETOF apt.atbd_reduced
  LANGUAGE sql
  IMMUTABLE
  AS $_$
  SELECT
    apt.atbds.atbd_id,
    apt.atbds.title,
    array_agg(apt.contacts.*) as contacts
  FROM apt.atbds
  FULL OUTER JOIN apt.atbd_contacts ON apt.atbd_contacts.atbd_id = apt.atbds.atbd_id
  FULL OUTER JOIN apt.contacts ON apt.contacts.contact_id = apt.atbd_contacts.contact_id
  WHERE apt.atbds.title LIKE searchstring
  OR CONCAT(apt.contacts.first_name, ' ', apt.contacts.last_name) LIKE searchstring
  GROUP BY apt.atbds.atbd_id;
  $_$;
COMMIT;
