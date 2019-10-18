-- Deploy nasa-apt:copyATBD to pg
-- requires: tables

BEGIN;

CREATE EXTENSION hstore;

CREATE FUNCTION copyATBD(orig_id integer, OUT new_id integer, OUT created_atbd apt.atbds)
AS $$
BEGIN
new_id := (select nextval(pg_get_serial_sequence('apt.atbds', 'atbd_id')));
INSERT INTO apt.atbds
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.atbds t WHERE atbd_id = orig_id
   ) sub RETURNING * INTO created_atbd;

INSERT INTO apt.atbd_versions
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.atbd_versions t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.citations
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.citations t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.data_access_input_data
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_input_data t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.data_access_output_data
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_output_data t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.data_access_related_urls
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.data_access_related_urls t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.publication_references
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.publication_references t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.algorithm_implementations
SELECT (t1).*
FROM  (
   SELECT t #= hstore('atbd_id', new_id::text) AS t1
   FROM   apt.algorithm_implementations t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.algorithm_input_variables
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('algorithm_input_variable_id', nextval(pg_get_serial_sequence('apt.algorithm_input_variables', 'algorithm_input_variable_id'))::text)) AS t1
   FROM   apt.algorithm_input_variables t WHERE atbd_id = orig_id
   ) sub;

INSERT INTO apt.algorithm_output_variables
SELECT (t1).*
FROM  (
   SELECT t #= (hstore('atbd_id', new_id::text) || hstore('algorithm_output_variable_id', nextval(pg_get_serial_sequence('apt.algorithm_output_variables', 'algorithm_output_variable_id'))::text)) AS t1
   FROM   apt.algorithm_output_variables t WHERE atbd_id = orig_id
   ) sub;

END;
$$
LANGUAGE PLPGSQL;

COMMIT;
