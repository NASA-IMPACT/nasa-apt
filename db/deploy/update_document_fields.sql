-- Deploy nasa-apt:update_document_fields to pg
BEGIN;
UPDATE
    apt.atbd_versions
SET
    document = document::jsonb || '{
        "abstract": null, 
        "additional_information": null, 
        "data_availability": null, 
        "algorithm_input_variables_caption": null,
        "algorithm_output_variables_caption": null
    }'::jsonb;
COMMIT;

