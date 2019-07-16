-- Deploy nasa-apt:contactsContraints to pg
-- requires: tables

BEGIN;
  alter TABLE apt.atbd_contacts
  drop CONSTRAINT atbd_contacts_atbd_id_fkey;
  alter TABLE apt.atbd_contacts
  add CONSTRAINT atbd_id
  FOREIGN KEY (atbd_id) REFERENCES apt.atbds(atbd_id)
  ON DELETE CASCADE;

  alter TABLE apt.atbd_contacts
  drop CONSTRAINT atbd_contacts_contact_id_fkey;
  alter TABLE apt.atbd_contacts
  add CONSTRAINT contact_id
  FOREIGN KEY (contact_id) REFERENCES apt.contacts(contact_id)
  ON DELETE CASCADE;

  alter TABLE apt.atbd_contact_groups
  drop CONSTRAINT atbd_contact_groups_atbd_id_fkey;
  alter TABLE apt.atbd_contact_groups
  add CONSTRAINT atbd_id
  FOREIGN KEY (atbd_id) REFERENCES apt.atbds(atbd_id)
  ON DELETE CASCADE;

  alter TABLE apt.atbd_contact_groups
  drop CONSTRAINT atbd_contact_groups_contact_group_id_fkey;
  alter TABLE apt.atbd_contact_groups
  add CONSTRAINT contact_group_id
  FOREIGN KEY (contact_group_id) REFERENCES apt.contact_groups(contact_group_id)
  ON DELETE CASCADE;

COMMIT;
