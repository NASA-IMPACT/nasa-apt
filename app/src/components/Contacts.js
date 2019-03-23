import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import ContactForm from './ContactForm';
import { createAtbdContact } from '../actions/actions';

const Contacts = (props) => {
  const {
    contacts,
    selectedAtbd,
    createAtbdContact: dispatchCreateAtbdContact
  } = props;
  const atbdContacts = selectedAtbd ? selectedAtbd.contacts : [];
  const contactOptions = contacts.map((contact) => {
    const {
      first_name,
      last_name,
      contact_id
    } = contact;
    return (
      <option
        key={contact_id}
        value={contact_id}
      >
        {`${first_name} ${last_name}`}
      </option>
    );
  });
  const atbdContactItems = atbdContacts.map((atbdContact) => {
    const {
      first_name,
      last_name,
      contact_id
    } = atbdContact;
    return (
      <li key={contact_id}>
        {`${first_name} ${last_name}`}
      </li>
    );
  });
  return (
    <Fragment>
      <span>Select an existing contact</span>
      <br />
      <select onChange={event => dispatchCreateAtbdContact({
        atbd_id: selectedAtbd.atbd_id,
        contact_id: event.target.value
      })
      }
      >
        {contactOptions}
      </select>
      <br />
      <span>Or create a new one</span>
      <br />
      <ContactForm />
      <br />
      <span>ATBD Contacts</span>
      <ul>
        {atbdContactItems}
      </ul>
    </Fragment>
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
    contacts: PropTypes.arrayOf(PropTypes.shape(contactShape))
  }),
  createAtbdContact: PropTypes.func.isRequired
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

const mapDispatchToProps = { createAtbdContact };

export default connect(mapStateToProps, mapDispatchToProps)(Contacts);
