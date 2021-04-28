-- Deploy nasa-apt:textsearchAlias to pg
-- requires: textsearch

BEGIN;

DROP FUNCTION apt.search_text(searchstring text, statusstring text);
DROP TYPE apt.atbd_reduced;

CREATE TYPE apt.atbd_reduced AS (
  atbd_id INTEGER,
  title VARCHAR (1024),
  alias VARCHAR (256),
  contacts apt.contacts[],
  atbd_versions apt.atbd_reduced_versions[]
);

CREATE FUNCTION apt.search_text(searchstring text default '',
  statusstring text default 'Draft,Published') returns SETOF apt.atbd_reduced
AS $$
  BEGIN
    RETURN QUERY
    SELECT
    apt.atbds.atbd_id,
    apt.atbds.title,
    apt.atbds.alias,
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
    AND (CASE WHEN searchstring = '' THEN TRUE
    ELSE (
        to_tsvector(apt.atbds.title) @@ plainto_tsquery(searchstring) OR
        to_tsvector(apt.atbds.alias) @@ plainto_tsquery(searchstring) OR
        to_tsvector(CONCAT(apt.contacts.first_name, ' ', apt.contacts.last_name)) @@ plainto_tsquery(searchstring)
      )
    END)
    GROUP BY apt.atbds.atbd_id;
  END
  $$ LANGUAGE plpgsql IMMUTABLE;

COMMIT;
