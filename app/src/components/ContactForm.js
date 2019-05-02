/* eslint camelcase: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import styled from 'styled-components';

import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';
import validateEmail from '../schemas/validateEmail';
import Select from './common/Select';
import Input, {
  InputFormGroup,
  InputSubmit
} from './common/Input';
import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
} from '../styles/form/fieldset';
import Form from '../styles/form/form';
import FormLegend from '../styles/form/legend';

const validator = new jsonschema.Validator();
const contactsSchema = addMinLength(apiSchema.definitions.contacts);
contactsSchema.required = contactsSchema
  .required.filter(property => (property !== 'contact_id'));

const first_name = 'first_name';
const middle_name = 'middle_name';
const last_name = 'last_name';
const uuid = 'uuid';
const url = 'url';
const contact_mechanism_type = 'contact_mechanism_type';
const contact_mechanism_types = contactsSchema
  .properties[contact_mechanism_type].enum;
const contact_mechanism_value = 'contact_mechanism_value';
const email = 'Email';

const SpanTwo = styled.div`
  grid-column-start: span 2;
`;

export const InnerContactForm = (props) => {
  const {
    values,
    touched,
    errors,
    handleChange,
    handleBlur,
    handleSubmit,
    id,
    contact,
    t
  } = props;
  const submitEnabled = !Object.keys(errors).length
                                  && Object.keys(touched).length;

  const submitValue = contact ? 'Update contact' : 'Create contact';
  return (
    <Form onSubmit={handleSubmit}>

      <InputFormGroup>
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
          info={t.person_uuid}
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
            info={t.person_related_url}
            optional
          />
        </SpanTwo>
      </InputFormGroup>

      <FormFieldset>
        <FormFieldsetHeader>
          <FormLegend>Contact Mechanism</FormLegend>
        </FormFieldsetHeader>
        <FormFieldsetBody>
          <InputFormGroup>
            <Select
              id={`${id}-contact-type`}
              name={contact_mechanism_type}
              label="Type"
              onChange={handleChange}
              onBlur={handleBlur}
              value={values[contact_mechanism_type]}
              error={errors[contact_mechanism_type]}
              touched={touched[contact_mechanism_type]}
              options={contact_mechanism_types.map(d => ({ value: d, label: d }))}
              info={t.person_mechanism_type}
            />
            <SpanTwo>
              <Input
                id={`${id}-contact-mechanism-value`}
                name={contact_mechanism_value}
                label="Value"
                type="text"
                onChange={handleChange}
                onBlur={handleBlur}
                value={values[contact_mechanism_value]}
                error={errors[contact_mechanism_value]}
                touched={touched[contact_mechanism_value]}
                info={t.person_mechanism_value}
              />
            </SpanTwo>
          </InputFormGroup>
        </FormFieldsetBody>
      </FormFieldset>

      <InputSubmit
        type="submit"
        disabled={!submitEnabled}
        value={submitValue}
      />
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

  contact: PropTypes.object,
  id: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string
  ]).isRequired,
  t: PropTypes.object
};

export const ContactForm = withFormik({
  mapPropsToValues: (props) => {
    const contact = props.contact || {};
    const initialValues = {
      [first_name]: contact.first_name || '',
      [middle_name]: contact.middle_name || '',
      [last_name]: contact.last_name || '',
      [uuid]: contact.uuid || '',
      [url]: contact.url || '',
      [contact_mechanism_type]: email,
      [contact_mechanism_value]: ''
    };
    return initialValues;
  },

  validate: (values) => {
    let errors = {};
    errors = transformErrors(
      validator.validate(values, contactsSchema).errors
    );
    if (values[contact_mechanism_type] === email) {
      const isValidEmail = validateEmail(values[contact_mechanism_value]);
      if (!isValidEmail) {
        errors[contact_mechanism_value] = 'Must be a valid email';
      }
    }
    return errors;
  },

  handleSubmit: (values, { props, setSubmitting, resetForm }) => {
    console.log(props);
    setSubmitting(false);
    resetForm();
  }
})(InnerContactForm);

const mapStateToProps = state => ({
  t: state.application.t ? state.application.t.contact_information : {}
});

const mapDispatchToProps = {};

export default connect(mapStateToProps, mapDispatchToProps)(ContactForm);
