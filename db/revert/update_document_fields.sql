-- Revert nasa-apt:update_document_fields from pg
BEGIN;
-- XXX Add DDLs here.
UPDATE
    apt.atbd_versions
SET
    document = document::jsonb #- '{abstract}' #- '{version_description}' #- '{data_availability}' #- '{additional_information}' #- '{algorithm_input_variables_caption}' #- '{algorithm_output_variables_caption}';

ALTER TABLE apt.atbd_versions
    ADD COLUMN changelog varchar default "";
COMMIT;

