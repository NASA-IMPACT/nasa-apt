-- Deploy nasa-apt:searcheverything to pg
-- requires: textsearchAlias
BEGIN;
SET SEARCH_PATH TO apt, public;

DROP VIEW IF EXISTS atbd_search CASCADE;
CREATE OR REPLACE VIEW atbd_search AS
SELECT
atbds.*,
json_agg(row_to_json(atbd_versions)) as atbd_versions,
json_agg(row_to_json(contacts)) as contacts,
json_agg(row_to_json(contact_groups)) as contact_groups,
json_agg(row_to_json(citations)) as citations,
json_agg(row_to_json(algorithm_input_variables)) as algorithm_input_variables,
json_agg(row_to_json(algorithm_output_variables)) as algorithm_output_variables,
json_agg(row_to_json(publication_references)) as publication_references,
json_agg(row_to_json(data_access_input_data)) as data_access_input_data,
json_agg(row_to_json(data_access_output_data)) as data_access_output_data,
json_agg(row_to_json(data_access_related_urls)) as data_access_related_urls,
to_tsvector(coalesce(atbds.title,'')) ||
json_to_tsvector(
    json_build_array(
        json_agg(row_to_json(atbd_versions)),
        json_agg(row_to_json(contacts)),
        json_agg(row_to_json(contact_groups)),
        json_agg(row_to_json(citations)),
        json_agg(row_to_json(algorithm_input_variables)),
        json_agg(row_to_json(algorithm_output_variables)),
        json_agg(row_to_json(publication_references)),
        json_agg(row_to_json(data_access_input_data)),
        json_agg(row_to_json(data_access_output_data)),
        json_agg(row_to_json(data_access_related_urls))
    ),
    '["string"]'
) as search
FROM
atbds
LEFT JOIN atbd_versions USING (atbd_id)
LEFT JOIN atbd_contacts USING
(atbd_id)
LEFT JOIN contacts USING (contact_id)
LEFT JOIN atbd_contact_groups USING (atbd_id)
LEFT JOIN contact_groups USING (contact_group_id)
LEFT JOIN citations USING (atbd_id, atbd_version)
LEFT JOIN algorithm_input_variables USING (atbd_id, atbd_version)
LEFT JOIN algorithm_output_variables USING (atbd_id, atbd_version)
LEFT JOIN algorithm_implementations USING (atbd_id, atbd_version)
LEFT JOIN publication_references USING (atbd_id, atbd_version)
LEFT JOIN data_access_input_data USING (atbd_id, atbd_version)
LEFT JOIN data_access_output_data USING (atbd_id, atbd_version)
LEFT JOIN data_access_related_urls USING (atbd_id, atbd_version)
GROUP BY atbd_id, atbd_version, status;


COMMIT;
