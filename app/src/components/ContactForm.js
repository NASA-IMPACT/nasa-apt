/* eslint camelcase: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';

import { createContact } from '../actions/actions';
import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';
import validateEmail from '../schemas/validateEmail';
import Select from './common/Select';
import Input, {
  InputFormGroup,
  InputSubmit
} from './common/Input';

const validator = new jsonschema.Validator();
const contactsSchema = addMinLength(apiSchema.definitions.contacts);
contactsSchema.required = contactsSchema
  .required.filter(property => (property !== 'contact_id'));

const first_name = 'first_name';
const middle_name = 'middle_name';
const last_name = 'last_name';
const contact_mechanism_type = 'contact_mechanism_type';
const contact_mechanism_types = contactsSchema
  .properties[contact_mechanism_type].enum;
const contact_mechanism_value = 'contact_mechanism_value';
const email = 'Email';

export const InnerContactForm = (props) => {
  const {
    values,
    touched,
    errors,
    handleChange,
    handleBlur,
    handleSubmit,
  } = props;
  const submitEnabled = !Object.keys(errors).length
                                  && Object.keys(touched).length;
  return (
    <InputFormGroup onSubmit={handleSubmit}>
      <Input
        id="cf-first-name"
        name={first_name}
        label="First Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[first_name]}
        error={errors[first_name]}
        touched={touched[first_name]}
        info="This is some info text. Awesome!"
      />
      <Input
        id="cf-middle-name"
        name={middle_name}
        label="Middle Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[middle_name]}
        error={errors[middle_name]}
        touched={touched[middle_name]}
      />
      <Input
        id="cf-last-name"
        name={last_name}
        label="Last Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[last_name]}
        error={errors[last_name]}
        touched={touched[last_name]}
      />
      <Select
        id="cf-contact-type"
        name={contact_mechanism_type}
        label="Contact Type"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[contact_mechanism_type]}
        error={errors[contact_mechanism_type]}
        touched={touched[contact_mechanism_type]}
        options={contact_mechanism_types.map(d => ({ value: d, label: d }))}
      />
      <Input
        id="cf-contact-mechanism-value"
        name={contact_mechanism_value}
        label="Contact"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[contact_mechanism_value]}
        error={errors[contact_mechanism_value]}
        touched={touched[contact_mechanism_value]}
      />
      <InputSubmit
        type="submit"
        disabled={!submitEnabled}
        value="Create Contact"
      />
    </InputFormGroup>
  );
};

InnerContactForm.propTypes = {
  values: PropTypes.object.isRequired,
  touched: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  handleChange: PropTypes.func.isRequired,
  handleBlur: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired
};

export const ContactForm = withFormik({
  mapPropsToValues: () => {
    const initialValues = {
      [first_name]: '',
      [middle_name]: '',
      [last_name]: '',
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
    const { createContact: create } = props;
    create(values);
    setSubmitting(false);
    resetForm();
  }
})(InnerContactForm);

const mapDispatchToProps = { createContact };

export default connect(null, mapDispatchToProps)(ContactForm);
