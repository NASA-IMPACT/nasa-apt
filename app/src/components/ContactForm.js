/* eslint camelcase: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import styled from 'styled-components/macro';
import { get, set } from 'object-path';

import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';
import validateEmail from '../schemas/validateEmail';
import Select from './common/Select';
import Input, { InputFormGroup } from './common/Input';
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
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import { FormCheckable } from '../styles/form/checkable';
import Form from '../styles/form/form';
import FormLegend from '../styles/form/legend';
import FormLabel from '../styles/form/label';
import FormToolbar from '../styles/form/toolbar';
import InfoButton from './common/InfoButton';
import Button from '../styles/button/button';
import AddBtn from '../styles/button/add';
import RemoveButton from '../styles/button/remove';

const validator = new jsonschema.Validator();

const contactsSchema = addMinLength(apiSchema.definitions.contacts);
contactsSchema.required = contactsSchema
  .required.filter(property => (property !== 'contact_id'));

const contactGroupsSchema = addMinLength(apiSchema.definitions.contact_groups);
contactGroupsSchema.required = contactGroupsSchema
  .required.filter(property => (property !== 'contact_group_id'));

const first_name = 'first_name';
const middle_name = 'middle_name';
const last_name = 'last_name';
const group_name = 'group_name';
const uuid = 'uuid';
const url = 'url';
const mechanism_type = 'mechanism_type';
const mechanism_value = 'mechanism_value';
const mechanisms = 'mechanisms';
const roles = 'roles';

const mechanismTypes = [
  'Direct line',
  'Email',
  'Facebook',
  'Fax',
  'Mobile',
  'Modem',
  'Primary',
  'TDD/TTY phone',
  'Telephone',
  'Twitter',
  'U.S.',
  'Other'
];

const roleTypes = [
  'Data center contact',
  'Technical contact',
  'Science contact',
  'Investigator',
  'Metadata author',
  'User services',
  'Science software development'
];

const SpanTwo = styled.div`
  grid-column-start: span 2;
`;

const SpanThree = styled.div`
  grid-column-start: span 3;
`;

export const InnerContactForm = (props) => {
  const {
    values,
    touched,
    errors,
    handleChange,
    handleBlur,
    handleSubmit,
    setValues,

    id,
    forceAllowSubmit,
    contact,
    isGroup,
    t
  } = props;
  const submitEnabled = !Object.keys(errors).length
    && (Object.keys(touched).length || forceAllowSubmit);

  let submitValue = forceAllowSubmit ? 'Attach contact'
    : contact ? 'Update contact' : 'Create contact';
  if (isGroup) {
    submitValue += ' group';
  }

  return (
    <Form onSubmit={handleSubmit}>
      <InputFormGroup>
        {isGroup ? (
          <SpanThree>
            <Input
              id={`${id}-group-name`}
              name={group_name}
              label="Group Name"
              type="text"
              onChange={handleChange}
              onBlur={handleBlur}
              value={values[group_name]}
              error={errors[group_name]}
              touched={touched[group_name]}
              info={t.group_name}
            />
          </SpanThree>
        ) : (
          <React.Fragment>
            <Input
              id={`${id}-first-name`}
              name={first_name}
              label="First Name"
              type="text"
              onChange={handleChange}
              onBlur={handleBlur}
              value={values[first_name]}
              error={errors[first_name]}
              touched={touched[first_name]}
              info={t.person_first_name}
            />
            <Input
              id={`${id}-middle-name`}
              name={middle_name}
              label="Middle Name"
              type="text"
              onChange={handleChange}
              onBlur={handleBlur}
              value={values[middle_name]}
              error={errors[middle_name]}
              touched={touched[middle_name]}
              info={t.person_middle_name}
              optional
            />
            <Input
              id={`${id}-last-name`}
              name={last_name}
              label="Last Name"
              type="text"
              onChange={handleChange}
              onBlur={handleBlur}
              value={values[last_name]}
              error={errors[last_name]}
              touched={touched[last_name]}
              info={t.person_last_name}
            />
          </React.Fragment>
        )}

        <Input
          id={`${id}-last-uuid`}
          name={uuid}
          label="UUID"
          type="text"
          onChange={handleChange}
          onBlur={handleBlur}
          value={values[uuid]}
          error={errors[uuid]}
          touched={touched[uuid]}
          info={isGroup ? t.group_uuid : t.person_uuid}
          optional
        />
        <SpanTwo>
          <Input
            id={`${id}-url`}
            name={url}
            label="URL"
            type="text"
            onChange={handleChange}
            onBlur={handleBlur}
            value={values[url]}
            error={errors[url]}
            touched={touched[url]}
            info={isGroup ? t.group_related_url : t.person_related_url}
            optional
          />
        </SpanTwo>
      </InputFormGroup>

      {!!errors.NO_MECHANISMS && (
        <FormFieldset>
          <FormFieldsetBody>
            <FormHelper>
              <FormHelperMessage>At least one contact mechanism is required.</FormHelperMessage>
            </FormHelper>
          </FormFieldsetBody>
        </FormFieldset>
      )}

      {(values[mechanisms] || []).map((d, i) => (
        /* eslint-disable react/no-array-index-key */
        <FormFieldset key={`mechanism-${i}`}>
          <FormFieldsetHeader>
            <FormLegend>Contact Mechanism #{i + 1}</FormLegend>
            <RemoveButton
              variation="base-plain"
              size="small"
              hideText
              onClick={() => {
                setValues({
                  ...values,
                  [mechanisms]: values[mechanisms].filter((_, idx) => i !== idx)
                });
                // Slightly hacky, but necessary to register a touch event
                // and remove the disabled state on the submit button.
                handleBlur({ target: { name: 'REMOVE' } });
              }}
            >
              Remove
            </RemoveButton>
          </FormFieldsetHeader>
          <FormFieldsetBody>
            <InputFormGroup>
              <Select
                id={`${id}-${i}-contact-type`}
                name={`mechanisms[${i}].${mechanism_type}`}
                label="Type"
                onChange={e => handleChange({
                  target: {
                    value: e.value,
                    name: `mechanisms[${i}].${mechanism_type}`
                  }
                })}
                onBlur={handleBlur}
                value={get(values, [mechanisms, i, mechanism_type])}
                touched={get(touched, [mechanisms, i, mechanism_type])}
                error={get(errors, [mechanisms, i, mechanism_type])}
                options={mechanismTypes.map(m => ({ value: m, label: m }))}
                info={isGroup ? t.group_mechanism_type : t.person_mechanism_type}
              />
              <SpanTwo>
                <Input
                  id={`${id}-${i}-contact-mechanism-value`}
                  name={`mechanisms[${i}].${mechanism_value}`}
                  label="Value"
                  type="text"
                  onChange={handleChange}
                  onBlur={handleBlur}
                  value={get(values, [mechanisms, i, mechanism_value])}
                  touched={get(touched, [mechanisms, i, mechanism_value])}
                  error={get(errors, [mechanisms, i, mechanism_value])}
                  info={isGroup ? t.group_mechanism_value : t.person_mechanism_value}
                />
              </SpanTwo>
            </InputFormGroup>
          </FormFieldsetBody>
        </FormFieldset>
      ))}

      <AddBtn
        variation="base-plain"
        onClick={() => setValues({
          ...values,
          [mechanisms]: values[mechanisms].concat([{
            [mechanism_type]: null,
            [mechanism_value]: ''
          }])
        })}
      >
        Add a contact mechanism
      </AddBtn>

      <FormGroup>
        <FormGroupHeader>
          <FormLabel>Role related to this document</FormLabel>
          <FormToolbar>
            <InfoButton text={isGroup ? t.group_role : t.person_role} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <InputFormGroup>
            {roleTypes.map((roleType, i) => (
              <FormCheckable
                key={`${id}-${i}-role-type`}
                id={`${id}-${i}-role-type`}
                type="checkbox"
                name={`roles[${i}]`}
                onChange={(e) => {
                  const name = `roles[${i}]`;
                  handleChange({ target: { name, value: e.target.checked } });
                  handleBlur({ target: { name } });
                }}
                checked={get(values, [roles, i])}
              >
                {roleType}
              </FormCheckable>
            ))}
          </InputFormGroup>
        </FormGroupBody>
      </FormGroup>

      <Button
        type="submit"
        variation="base-raised-light"
        size="large"
        disabled={!submitEnabled}
      >
        {submitValue}
      </Button>
    </Form>
  );
};

InnerContactForm.propTypes = {
  values: PropTypes.object.isRequired,
  touched: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  handleChange: PropTypes.func.isRequired,
  handleBlur: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  setValues: PropTypes.func.isRequired,

  contact: PropTypes.object,
  id: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired,

  t: PropTypes.object,
  isGroup: PropTypes.bool,
  forceAllowSubmit: PropTypes.bool,

  /* eslint-disable react/no-unused-prop-types */
  save: PropTypes.func
};

export const ContactForm = withFormik({
  mapPropsToValues: (props) => {
    const { isGroup } = props;
    const contact = props.contact || {};
    const contactRoles = contact.roles || [];
    const nameField = isGroup ? { [group_name]: contact[group_name] || '' }
      : {
        [first_name]: contact.first_name || '',
        [middle_name]: contact.middle_name || '',
        [last_name]: contact.last_name || '',
      };
    const initialValues = {
      [uuid]: contact.uuid || '',
      [url]: contact.url || '',
      [mechanisms]: contact.mechanisms || [],
      [roles]: roleTypes.map(r => contactRoles.indexOf(r) >= 0),
      ...nameField
    };
    if (!initialValues[mechanisms].length) {
      initialValues[mechanisms].push({
        mechanism_type: null,
        mechanism_value: ''
      });
    }
    return initialValues;
  },

  validate: (values, { isGroup }) => {
    const schema = isGroup ? contactGroupsSchema : contactsSchema;
    let errors = {};
    errors = transformErrors(
      validator.validate(values, schema).errors
    );

    // Validate existing mechanism types and values are not null.
    // Also validate email addresses.
    // TODO: validate other mechanisms such as phone numbers.
    values[mechanisms].forEach((mechanism, i) => {
      if (!mechanism[mechanism_type]) {
        set(errors, [mechanisms, i, mechanism_type], 'Must select a contact mechanism');
      }
      if (!mechanism[mechanism_value]) {
        set(errors, [mechanisms, i, mechanism_value], 'Must enter a contact');
      }
      if (mechanism[mechanism_type] === 'Email') {
        const isValidEmail = validateEmail(mechanism[mechanism_value]);
        if (!isValidEmail) {
          set(errors, [mechanisms, i, mechanism_value], 'Must be valid email');
        }
      }
    });
    // Also slightly hacky, this is a flag for the UI to show that at least 1
    // mechanism is required.
    if (!values[mechanisms].length) {
      set(errors, 'NO_MECHANISMS', true);
    }
    return errors;
  },

  handleSubmit: (values, { props, setSubmitting, resetForm }) => {
    const { save } = props;
    const payload = {
      ...values,
      mechanisms: formatPostgresArray(values.mechanisms.map(formatMechanism)),
      roles: formatPostgresArray(values.roles.map((active, idx) => (
        active && roleTypes[idx]
      )).filter(Boolean))
    };
    save(payload);
    setSubmitting(false);
    resetForm();
  },

  // re-render when props change
  enableReinitialize: true
})(InnerContactForm);

function formatMechanism(mechanism) {
  return `(\\"${mechanism[mechanism_type]}\\",\\"${mechanism[mechanism_value]}\\")`;
}

// ['foo', 'bar'] => '{ "foo", "bar" }'
function formatPostgresArray(array) {
  if (!Array.isArray(array) || !array.length) return '{ }';
  return `{ ${array.map(d => `"${d}"`).join(', ')} }`;
}

const mapStateToProps = state => ({
  t: state.application.t ? state.application.t.contact_information : {}
});

const mapDispatchToProps = {};

export default connect(mapStateToProps, mapDispatchToProps)(ContactForm);
