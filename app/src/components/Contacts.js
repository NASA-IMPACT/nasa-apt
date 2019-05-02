import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import uuid from 'uuid';

import ContactFormWrapper from './ContactFormWrapper';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import AddBtn from '../styles/button/add';

import {
  deleteAtbdContact
} from '../actions/actions';

class Contacts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      contacts: []
    };
    this.addContact = this.addContact.bind(this);
    this.removeContact = this.removeContact.bind(this);
  }

  addContact() {
    const { contacts } = this.state;
    const next = contacts.concat([uuid()]);
    this.setState({ contacts: next });
  }

  removeContact(id) {
    const { contacts } = this.state;
    const next = contacts.filter(d => d !== id);
    this.setState({ contacts: next });
  }

  render() {
    const {
      allContacts,
      selectedAtbd,
      deleteAtbdContact: deleteContact
    } = this.props;

    let returnValue;
    if (selectedAtbd) {
      const {
        atbd_id,
        title
      } = selectedAtbd;

      const {
        addContact,
        removeContact
      } = this;

      const {
        contacts: newContacts
      } = this.state;

      const atbdContacts = selectedAtbd.contacts || [];

      // Remove any contacts that are already attached
      let availableContacts = allContacts;
      if (atbdContacts.length) {
        const existingContacts = atbdContacts.map(d => d.contact_id);
        availableContacts = allContacts.filter(d => existingContacts.indexOf(d.contact_id) === -1);
      }

      returnValue = (
        <Inpage>
          <EditPage
            title={title || ''}
            id={atbd_id}
            step={3}
          >
            <h2>Contacts</h2>
            {atbdContacts.map((d, i) => (
              <ContactFormWrapper
                key={d.contact_id}
                id={d.contact_id}
                title={`Contact #${i + 1}`}
                contact={d}
                contacts={allContacts}
                onRemove={() => deleteContact(atbd_id, d.contact_id)}
              />
            ))}

            {newContacts.map(d => (
              <ContactFormWrapper
                key={d}
                id={d}
                title="New contact"
                contacts={availableContacts}
                onRemove={() => removeContact(d)}
              />
            ))}

            <AddBtn
              variation="base-plain"
              onClick={addContact}
            >
              Add a contact
            </AddBtn>
          </EditPage>
        </Inpage>
      );
    } else {
      returnValue = <div>Loading</div>;
    }
    return returnValue;
  }
}

const contactShape = PropTypes.shape({
  contact_id: PropTypes.number.isRequired,
  first_name: PropTypes.string.isRequired,
  last_name: PropTypes.string.isRequired,
});

Contacts.propTypes = {
  allContacts: PropTypes.arrayOf(contactShape),
  selectedAtbd: PropTypes.shape({
    atbd_id: PropTypes.number.isRequired
  }),
  deleteAtbdContact: PropTypes.func
};

const mapStateToProps = state => ({
  allContacts: state.application.contacts || [],
  selectedAtbd: state.application.selectedAtbd
});

const mapDispatch = {
  deleteAtbdContact
};

export default connect(mapStateToProps, mapDispatch)(Contacts);
