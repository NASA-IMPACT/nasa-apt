-- Deploy nasa-apt:notifytriggers to pg

BEGIN;
SET SEARCH_PATH to apt, public;

CREATE OR REPLACE FUNCTION change_notification() RETURNS TRIGGER AS $$
DECLARE
BEGIN
PERFORM pg_notify('atbd',NEW.atbd_id::text);
RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

CREATE TRIGGER atbd_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.atbds FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER atbd_versions_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.atbd_versions FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER citations_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.citations FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER algorithm_input_variables_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.algorithm_input_variables FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER algorithm_output_variables_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.algorithm_output_variables FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER publication_references_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.publication_references FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER data_access_input_data_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.data_access_input_data FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER data_access_output_data_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.data_access_output_data FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();
CREATE TRIGGER data_access_related_urls_notify_change AFTER INSERT OR UPDATE OR DELETE ON apt.data_access_related_urls FOR EACH ROW EXECUTE PROCEDURE apt.change_notification();








COMMIT;
