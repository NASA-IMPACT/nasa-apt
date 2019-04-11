import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import ContactForm from './ContactForm';
import {
  Inpage
} from './common/Inpage';
import EditPage, {
  EditorSection,
  EditorLabel,
} from './common/EditPage';
import RemovableListItem from './common/RemovableListItem';
import { createAtbdContact, deleteAtbdContact } from '../actions/actions';

import Select from './common/Select';

const Contacts = (props) => {
  const {
    contacts,
    selectedAtbd = {},
    createAtbdContact: dispatchCreateAtbdContact,
    deleteAtbdContact: dispatchDeleteAtbdContact
  } = props;

  const {
    atbd_id,
    title
  } = selectedAtbd;

  const atbdContacts = selectedAtbd.contacts || [];

  const contactOptions = contacts.map((contact) => {
    const {
      first_name,
      last_name,
      contact_id
    } = contact;
    return { label: `${first_name} ${last_name}`, value: contact_id };
  });

  const atbdContactItems = atbdContacts.map((atbdContact) => {
    const {
      first_name,
      last_name,
      contact_id
    } = atbdContact;
    return (
      <RemovableListItem
        key={contact_id}
        label={`${first_name} ${last_name}`}
        deleteAction={() => { dispatchDeleteAtbdContact(atbd_id, contact_id); }}
      />
    );
  });

  return (
    <Inpage>
      <EditPage
        title={title || ''}
        id={atbd_id}
        step={3}
        numSteps={7}
      >
        <h2>Contacts</h2>
        <EditorSection>
          <EditorLabel>Existing contacts</EditorLabel>
          <Select
            name="existing-contact"
            label="Select contact"
            options={contactOptions}
            onChange={e => dispatchCreateAtbdContact({
              atbd_id: selectedAtbd.atbd_id,
              contact_id: e.target.value
            })}
          />
        </EditorSection>

        <EditorSection>
          <EditorLabel>Create new contacts</EditorLabel>
          <ContactForm />
        </EditorSection>

        <EditorSection>
          <EditorLabel>ATBD contacts</EditorLabel>
          <ul>
            {atbdContactItems}
          </ul>
        </EditorSection>
      </EditPage>
    </Inpage>
  );
};

const contactShape = PropTypes.shape({
  contact_id: PropTypes.number.isRequired,
  first_name: PropTypes.string.isRequired,
  last_name: PropTypes.string.isRequired
});

Contacts.propTypes = {
  contacts: PropTypes.arrayOf(contactShape),
  selectedAtbd: PropTypes.shape({
    atbd_id: PropTypes.number.isRequired,
    contacts: PropTypes.array
  }),
  createAtbdContact: PropTypes.func.isRequired,
  deleteAtbdContact: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const {
    contacts,
    selectedAtbd
  } = state.application;

  return {
    contacts,
    selectedAtbd
  };
};

const mapDispatchToProps = { createAtbdContact, deleteAtbdContact };

export default connect(mapStateToProps, mapDispatchToProps)(Contacts);
