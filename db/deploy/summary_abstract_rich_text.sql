-- Deploy nasa-apt:summary_abstract_rich_text to pg
BEGIN;
-- convert 'abstract' and 'plain_summary' fields of document column to rich text objects.
-- Eg: {... 'abstract': 'text'...} --> {"abstract": {"children": [{"type": "p", "children": [{"text": "Existing text"}]}]}
-- The document object gets cast to jsonb to make use of the concatenate (||) operator
UPDATE
    atbd_versions
SET
    document = document::jsonb || json_build_object('abstract', json_build_object('children', json_build_array(json_build_object('type', 'p', 'children', json_build_array(json_build_object('text', document -> 'abstract'))))))::jsonb
WHERE
    document ->> 'abstract' IS NOT NULL;
UPDATE
    atbd_versions
SET
    document = document::jsonb || json_build_object('plain_summary', json_build_object('children', json_build_array(json_build_object('type', 'p', 'children', json_build_array(json_build_object('text', document -> 'plain_summary'))))))::jsonb
WHERE
    document ->> 'plain_summary' IS NOT NULL;
COMMIT;

