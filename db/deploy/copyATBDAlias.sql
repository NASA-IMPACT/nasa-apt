-- Deploy nasa-apt:copyATBDAlias to pg
-- requires: copyATBD

BEGIN;

DROP FUNCTION apt.copy_atbd(originalid integer, OUT new_id integer, OUT created_atbd apt.atbds);

CREATE FUNCTION apt.copy_atbd(originalid integer, OUT new_id integer, OUT created_atbd apt.atbds)
AS $$
DECLARE
new_title text;
alias_count integer;
current_alias text;
new_alias text;
BEGIN
new_id := (select nextval(pg_get_serial_sequence('apt.atbds', 'atbd_id')));
new_title = (select CONCAT('Copy of ', title) from apt.atbds where atbd_id = originalid);
-- Append a count to the curent alias to create a different one.
current_alias = (select alias from apt.atbds where atbd_id = originalid);
alias_count = (select count(atbd_id) from apt.atbds where alias like CONCAT(current_alias, '-%'));
new_alias = (select CONCAT(current_alias, '-', alias_count + 1));
INSERT INTO apt.atbds
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('title', new_title) || hstore('alias', new_alias)) AS t1
   FROM   apt.atbds t WHERE atbd_id = originalid
   ) sub RETURNING * INTO created_atbd;

INSERT INTO apt.atbd_versions
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('status', 'Draft')) AS t1
   FROM   apt.atbd_versions t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.citations
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.citations t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.atbd_contacts
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.atbd_contacts t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.data_access_input_data
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_input_data t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.data_access_output_data
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_output_data t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.data_access_related_urls
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_related_urls t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.publication_references
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.publication_references t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.algorithm_implementations
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.algorithm_implementations t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.algorithm_input_variables
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('algorithm_input_variable_id', nextval(pg_get_serial_sequence('apt.algorithm_input_variables', 'algorithm_input_variable_id'))::text)) AS t1
   FROM   apt.algorithm_input_variables t WHERE atbd_id = originalid
   ) sub;

INSERT INTO apt.algorithm_output_variables
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('algorithm_output_variable_id', nextval(pg_get_serial_sequence('apt.algorithm_output_variables', 'algorithm_output_variable_id'))::text)) AS t1
   FROM   apt.algorithm_output_variables t WHERE atbd_id = originalid
   ) sub;

END;
$$
LANGUAGE PLPGSQL;

COMMIT;
