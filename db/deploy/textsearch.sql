-- Deploy nasa-apt:textsearch to pg
-- requires: atbdConstraint
-- requires: tables

BEGIN;
CREATE TYPE apt.atbd_reduced_versions AS (
  atbd_id INTEGER,
  atbd_version INTEGER,
  status apt.atbd_status
);
CREATE TYPE apt.atbd_reduced AS (
  atbd_id INTEGER,
  title VARCHAR (1024),
  contacts apt.contacts[],
  atbd_versions apt.atbd_reduced_versions[]
);

CREATE FUNCTION apt.search_text(searchstring text default '%',
  statusstring text default 'Draft,Published') returns SETOF apt.atbd_reduced
  LANGUAGE sql
  IMMUTABLE
  AS $_$
  SELECT
    apt.atbds.atbd_id,
    apt.atbds.title,
    array_agg(apt.contacts.*) as contacts,
    array_agg(
      ROW(
        apt.atbd_versions.atbd_id, apt.atbd_versions.atbd_version, apt.atbd_versions.status)
        ::apt.atbd_reduced_versions
      )
        AS atbd_versions
  FROM apt.atbds
  FULL OUTER JOIN apt.atbd_versions ON apt.atbd_versions.atbd_id = apt.atbds.atbd_id
  FULL OUTER JOIN apt.atbd_contacts ON apt.atbd_contacts.atbd_id = apt.atbds.atbd_id
  FULL OUTER JOIN apt.contacts ON apt.contacts.contact_id = apt.atbd_contacts.contact_id
  WHERE apt.atbd_versions.status = ANY (regexp_split_to_array(statusstring, ',')::apt.atbd_status[])
  AND (apt.atbds.title LIKE searchstring
  OR CONCAT(apt.contacts.first_name, ' ', apt.contacts.last_name) LIKE searchstring)
  GROUP BY apt.atbds.atbd_id;
  $_$;
COMMIT;
