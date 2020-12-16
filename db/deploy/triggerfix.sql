-- Deploy nasa-apt:triggerfix to pg

BEGIN;

SET SEARCH_PATH to apt, public;

CREATE OR REPLACE FUNCTION change_notification() RETURNS TRIGGER AS $$
DECLARE
_atbd_id int;
BEGIN
IF TG_TABLE_NAME = 'contacts' THEN
    SELECT INTO _atbd_id atbd_id from atbd_contacts WHERE contact_id=NEW.contact_id;
ELSIF TG_TABLE_NAME = 'contact_groups' THEN
    SELECT INTO _atbd_id atbd_id from atbd_contact_groups WHERE contact_group_id=NEW.contact_group_id;
ELSE
    _atbd_id = NEW.atbd_id;
END IF;
PERFORM pg_notify('atbd',_atbd_id::text);
RETURN NEW;
END;
$$ LANGUAGE PLPGSQL;

COMMIT;
