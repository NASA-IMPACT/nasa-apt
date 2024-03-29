-- Revert nasa-apt:summary_abstract_rich_text from pg
BEGIN;
-- XXX Add DDLs here.
UPDATE
    apt.atbd_versions
SET
    document = document::jsonb || json_build_object('abstract', document -> 'abstract' -> 'children' -> 0 -> 'children' -> 0 -> 'text')::jsonb
WHERE
    document ->> 'abstract' IS NOT NULL;
UPDATE
    apt.atbd_versions
SET
    document = document::jsonb || json_build_object('plain_summary', document -> 'plain_summary' -> 'children' -> 0 -> 'children' -> 0 -> 'text')::jsonb
WHERE
    document ->> 'plain_summary' IS NOT NULL;
COMMIT;

