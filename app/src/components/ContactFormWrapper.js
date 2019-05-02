/* eslint camelcase: 0 */
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  createAtbdContact,
  createContact
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
    let type = null;
    if (contact) {
      // group contacts will have `contact_group_id`.
      type = contact.contact_id ? PERSON : GROUP;
    }
    this.state = {
      selectValue: contact && contact.contact_id,
      type
    };
    this.onSelectChange = this.onSelectChange.bind(this);
    this.onTypeChange = this.onTypeChange.bind(this);
  }

  onSelectChange({ value, type }) {
    const next = { selectValue: value };
    if (value !== NEW && type) {
      next.type = type;
    }
    this.setState(next);
  }

  onTypeChange(type) {
    this.setState({ type });
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
      selectValue,
      type
    } = this.state;
    const {
      contact: existingContact,
      contacts,
      id
    } = this.props;

    let contact = existingContact;
    // Prefill the contact form from all available contacts
    if (!existingContact && selectValue !== NEW) {
      contact = contacts.find((d) => {
        const { contact_id, contact_group_id } = d;
        return selectValue === contact_id || selectValue === contact_group_id;
      });
    }

    return (
      <ContactForm contact={contact} id={id} type={type} />
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
      selectValue,
      type
    } = this.state;

    const readonly = !!contact;
    const label = readonly ? 'Edit existing' : 'New or existing';

    // TODO better display labeling
    const selectOptions = contacts.map(d => ({
      value: d.contact_id || d.contact_group_id,
      label: d.first_name,
      type: d.contact_id ? PERSON : GROUP
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
            value={selectValue}
            onChange={onSelectChange}
            readonly={readonly}
          />
          {!!selectValue && this.renderTypePicker()}
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
  onRemove: PropTypes.func.isRequired
};

const mapDispatch = {
  createAtbdContact,
  createContact
};

export default connect(null, mapDispatch)(ContactFormWrapper);
