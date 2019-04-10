import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import styled from 'styled-components';
import ReactTooltip from 'react-tooltip';

import { themeVal } from '../styles/utils/general';
import collecticon from '../styles/collecticons';

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

import FormGroup from '../styles/molecules/form/group';
import FormToolbar from '../styles/molecules/form/toolbar';
import FormLabel from '../styles/atoms/form/label';

import Button from '../styles/atoms/button';
import Select from './Select';

const InfoButton = styled(Button)`
  ::before {
    ${collecticon('circle-information')}
  }
`;

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
          <FormGroup>
            <FormLabel>Existing contacts</FormLabel>
            <FormToolbar>
              <InfoButton variation='base-plain' size='small' hideText data-tip='Lorem ipsum dolor sit amet.'>Learn more</InfoButton>
              <ReactTooltip effect='solid' className='type-primary' />
            </FormToolbar>
            <Select
              name="existing-contact"
              options={contactOptions}
              onChange={e => dispatchCreateAtbdContact({
                atbd_id: selectedAtbd.atbd_id,
                contact_id: e.target.value
              })}
            />
          </FormGroup>
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
