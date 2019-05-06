/* eslint camelcase: 0 */
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  createAtbdContact,
  createContact,
  updateContact,
  createAtbdContactGroup,
  createContactGroup,
  updateContactGroup
} from '../actions/actions';

import Select from './common/Select';
import FormLegend from '../styles/form/legend';
import FormLabel from '../styles/form/label';
import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
} from '../styles/form/fieldset';
import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import {
  FormCheckable,
  FormCheckableGroup
} from '../styles/form/checkable';
import RemoveButton from '../styles/button/remove';

import ContactForm from './ContactForm';

const NEW = 'new';
const PERSON = 'person';
const GROUP = 'group';

class ContactFormWrapper extends Component {
  constructor(props) {
    super(props);
    const { contact } = props;
    let selectedContact = null;
    let type = null;
    if (contact) {
      selectedContact = contact.id;
      type = contact.isGroup ? GROUP : PERSON;
    }
    this.state = {
      selectedContact,
      type
    };
    this.onSelectChange = this.onSelectChange.bind(this);
    this.onTypeChange = this.onTypeChange.bind(this);
    this.save = this.save.bind(this);
  }

  componentDidUpdate(prevProps) {
    const {
      lastCreatedContact,
      selectedAtbd,
      createAtbdContact: attachContact,
      createAtbdContactGroup: attachContactGroup
    } = this.props;

    const { lastCreatedContact: prev } = prevProps;
    if (lastCreatedContact !== prev) {
      const { atbd_id } = selectedAtbd;
      // Attach this contact to the current atbd.
      const idProperty = lastCreatedContact.isGroup
        ? 'contact_group_id' : 'contact_id';
      const attachFn = lastCreatedContact.isGroup
        ? attachContactGroup : attachContact;
      const payload = {
        atbd_id,
        [idProperty]: lastCreatedContact[idProperty]
      };
      attachFn(payload);
    }
  }

  onSelectChange({ value, type }) {
    const next = { selectedContact: value };
    if (value !== NEW && type) {
      next.type = type;
    } else if (value === NEW) {
      next.type = null;
    }
    this.setState(next);
  }

  onTypeChange(type) {
    this.setState({ type });
  }

  save(payload) {
    const {
      selectedContact,
      type
    } = this.state;
    const {
      selectedAtbd,
      contact,
      createContactGroup, // eslint-disable-line no-shadow
      createContact, // eslint-disable-line no-shadow
      updateContactGroup, // eslint-disable-line no-shadow
      updateContact, // eslint-disable-line no-shadow
      createAtbdContact: attachContact,
      createAtbdContactGroup: attachContactGroup,
      onRemove
    } = this.props;

    if (selectedContact === NEW) {
      // Create a wholly new contact or contact group
      const saveFn = type === GROUP ? createContactGroup : createContact;
      saveFn(payload);
      onRemove();
    } else {
      // Patch the existing contact or contact group,
      // and if necessary, link it to this ATBD.
      const updateFn = type === GROUP ? updateContactGroup : updateContact;
      const id = selectedContact.slice(1, selectedContact.length);
      updateFn(id, payload);

      if (!contact) {
        const attachFn = type === GROUP
          ? attachContactGroup : attachContact;
        const { atbd_id } = selectedAtbd;
        attachFn({
          [type === GROUP ? 'contact_group_id' : 'contact_id']: id,
          atbd_id
        });
        onRemove();
      }
    }
  }

  renderTypePicker() {
    const { onTypeChange } = this;
    const { id } = this.props;
    const { type } = this.state;
    return (
      <FormGroup>
        <FormGroupHeader>
          <FormLabel>Type</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormCheckableGroup>
            <FormCheckable
              checked={type === PERSON}
              type="radio"
              name={`${id}-radio`}
              id={`${id}-type-person`}
              onChange={() => onTypeChange(PERSON)}
            >
              Person
            </FormCheckable>
            <FormCheckable
              checked={type === GROUP}
              type="radio"
              name={`${id}-radio`}
              id={`${id}-type-group`}
              onChange={() => onTypeChange(GROUP)}
            >
              Group
            </FormCheckable>
          </FormCheckableGroup>
        </FormGroupBody>
      </FormGroup>
    );
  }

  renderForm() {
    const {
      selectedContact,
      type
    } = this.state;
    const {
      contact,
      contacts,
      id
    } = this.props;
    const {
      save
    } = this;

    let data = contact;
    let isExistingContact = false;

    // This scenario means someone has chosen an existing contact
    // to add to this ATBD (and possibly to edit the existing contact).
    if (!data && selectedContact !== NEW) {
      data = contacts.find(d => selectedContact === d.id);
      isExistingContact = true;
    }

    return (
      <ContactForm
        contact={data}
        id={id}
        isGroup={type === GROUP}
        save={save}
        forceAllowSubmit={isExistingContact}
      />
    );
  }

  render() {
    const {
      onSelectChange
    } = this;

    const {
      title,
      id,
      contact,
      contacts,
      onRemove
    } = this.props;

    const {
      selectedContact,
      type
    } = this.state;

    const readonly = !!contact;
    const label = readonly ? 'Edit existing' : 'New or existing';
    const selectOptions = contacts.map(d => ({
      value: d.id,
      label: d.displayName,
      type: d.isGroup ? GROUP : PERSON
    }));

    selectOptions.unshift({
      value: NEW,
      label: 'New contact'
    });

    return (
      <FormFieldset>
        <FormFieldsetHeader>
          <FormLegend>{title}</FormLegend>
          <RemoveButton
            variation="base-plain"
            size="small"
            hideText
            onClick={onRemove}
          >
            Remove
          </RemoveButton>
        </FormFieldsetHeader>
        <FormFieldsetBody>
          <Select
            name={`${id}-select`}
            id={`${id}-select`}
            label={label}
            options={selectOptions}
            value={selectedContact}
            onChange={onSelectChange}
            readonly={readonly}
          />
          {selectedContact === NEW && this.renderTypePicker()}
          {!!type && this.renderForm()}
        </FormFieldsetBody>
      </FormFieldset>
    );
  }
}

ContactFormWrapper.propTypes = {
  title: PropTypes.string.isRequired,
  id: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired,
  contact: PropTypes.object,
  contacts: PropTypes.array,
  onRemove: PropTypes.func.isRequired,

  selectedAtbd: PropTypes.object,
  lastCreatedContact: PropTypes.object,
  createAtbdContact: PropTypes.func,
  createContact: PropTypes.func,
  updateContact: PropTypes.func,
  createAtbdContactGroup: PropTypes.func,
  createContactGroup: PropTypes.func,
  updateContactGroup: PropTypes.func
};

const mapStateToProps = state => ({
  selectedAtbd: state.application.selectedAtbd,
  lastCreatedContact: state.application.lastCreatedContact
});

const mapDispatch = {
  createAtbdContact,
  createContact,
  updateContact,
  createAtbdContactGroup,
  createContactGroup,
  updateContactGroup
};

export default connect(mapStateToProps, mapDispatch)(ContactFormWrapper);
