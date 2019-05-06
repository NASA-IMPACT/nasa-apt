import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import uuid from 'uuid';

import ContactFormWrapper from './ContactFormWrapper';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import AddBtn from '../styles/button/add';

import {
  deleteAtbdContact,
  deleteAtbdContactGroup
} from '../actions/actions';

class Contacts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      contacts: []
    };
    this.addContact = this.addContact.bind(this);
    this.removeContact = this.removeContact.bind(this);
    this.deleteContactOrGroup = this.deleteContactOrGroup.bind(this);
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

  deleteContactOrGroup(contactOrGroup) {
    const {
      deleteAtbdContact: deleteContact,
      deleteAtbdContactGroup: deleteContactGroup,
      selectedAtbd
    } = this.props;
    const { atbd_id } = selectedAtbd;
    const deleteFn = contactOrGroup.isGroup ? deleteContactGroup : deleteContact;
    const id = contactOrGroup.isGroup ? contactOrGroup.contact_group_id
      : contactOrGroup.contact_id;
    deleteFn(atbd_id, id);
  }

  render() {
    const {
      allContacts,
      allContactGroups,
      selectedAtbd
    } = this.props;

    let returnValue;
    if (selectedAtbd) {
      const {
        atbd_id,
        title
      } = selectedAtbd;

      const {
        addContact,
        removeContact,
        deleteContactOrGroup
      } = this;

      const {
        contacts: newContacts
      } = this.state;

      // Combine contacts and contact groups
      const atbdContacts = selectedAtbd.contacts.concat(selectedAtbd.contact_groups);
      const contactsAndGroups = allContacts.concat(allContactGroups)
        .sort((a, b) => a.displayName < b.displayName ? -1 : 1);

      // Remove any contacts that are already attached
      let availableContacts = [...contactsAndGroups];
      if (atbdContacts.length) {
        const existingContacts = atbdContacts.map(d => d.id);
        availableContacts = contactsAndGroups.filter(d => existingContacts.indexOf(d.id) === -1);
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
                key={d.id}
                id={d.id}
                title={`Contact #${i + 1}`}
                contact={d}
                contacts={contactsAndGroups}
                onRemove={() => deleteContactOrGroup(d)}
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
  allContactGroups: PropTypes.array,
  selectedAtbd: PropTypes.shape({
    atbd_id: PropTypes.number.isRequired
  }),
  deleteAtbdContact: PropTypes.func,
  deleteAtbdContactGroup: PropTypes.func
};

const mapStateToProps = state => ({
  allContacts: state.application.contacts || [],
  allContactGroups: state.application.contact_groups || [],
  selectedAtbd: state.application.selectedAtbd
});

const mapDispatch = {
  deleteAtbdContact,
  deleteAtbdContactGroup
};

export default connect(mapStateToProps, mapDispatch)(Contacts);
