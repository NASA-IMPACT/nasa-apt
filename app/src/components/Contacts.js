import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import ContactForm from './ContactForm';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import RemovableListItem from './common/RemovableListItem';
import Form from '../styles/form/form';
import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
} from '../styles/form/fieldset';
import FormLegend from '../styles/form/legend';
import { createAtbdContact, deleteAtbdContact } from '../actions/actions';

import Select from './common/Select';

const Contacts = (props) => {
  const {
    contacts,
    selectedAtbd,
    createAtbdContact: dispatchCreateAtbdContact,
    deleteAtbdContact: dispatchDeleteAtbdContact,
    t
  } = props;
  let returnValue;
  if (selectedAtbd) {
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

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={3}
        >
          <h2>Contacts</h2>
          <Form>
            <FormFieldset>
              <FormFieldsetHeader>
                <FormLegend>Existing contacts</FormLegend>
              </FormFieldsetHeader>
              <FormFieldsetBody>
                <Select
                  name="existing-contact"
                  label="Select contact"
                  options={contactOptions}
                  onChange={e => dispatchCreateAtbdContact({
                    atbd_id: selectedAtbd.atbd_id,
                    contact_id: e.target.value
                  })}
                  info={t.contact}
                />
              </FormFieldsetBody>
            </FormFieldset>
          </Form>

          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Create new contacts</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <ContactForm />
            </FormFieldsetBody>
          </FormFieldset>

          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Existing contacts</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <ul>
                {atbdContactItems}
              </ul>
            </FormFieldsetBody>
          </FormFieldset>
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = <div>Loading</div>;
  }
  return returnValue;
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
  deleteAtbdContact: PropTypes.func.isRequired,
  t: PropTypes.object
};

const mapStateToProps = (state) => {
  const {
    contacts,
    selectedAtbd,
    t
  } = state.application;

  return {
    contacts,
    selectedAtbd,
    t: t ? t.contact_information : {}
  };
};

const mapDispatchToProps = { createAtbdContact, deleteAtbdContact };

export default connect(mapStateToProps, mapDispatchToProps)(Contacts);
