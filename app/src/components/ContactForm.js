/* eslint camelcase: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';
import Input from './Input';
import Select from './Select';

const validator = new jsonschema.Validator();
const contactsSchema = addMinLength(apiSchema.definitions.contacts);
const first_name = 'first_name';
const middle_name = 'middle_name';
const last_name = 'last_name';
const contact_mechanism_type = 'contact_mechanism_type';
const contact_mechanism_types = contactsSchema
  .properties[contact_mechanism_type].enum;

const InnerContactForm = (props) => {
  const {
    values,
    touched,
    errors,
    handleChange,
    handleBlur,
    handleSubmit,
  } = props;

  return (
    <form onSubmit={handleSubmit}>
      <Input
        name={first_name}
        label="First Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[first_name]}
        error={errors[first_name]}
        touched={touched[first_name]}
      />
      <Input
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
        name={contact_mechanism_type}
        label="Contact Mechanism Type"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[contact_mechanism_type]}
        error={errors[contact_mechanism_type]}
        touched={touched[contact_mechanism_type]}
        options={contact_mechanism_types}
      />
      <button type="submit">Submit</button>
    </form>
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
      [contact_mechanism_type]: 'Email'
    };
    return initialValues;
  },

  validate: (values) => {
    let errors = {};
    errors = transformErrors(
      validator.validate(values, contactsSchema).errors
    );
    return errors;
  },

  handleSubmit: (values, { setSubmitting }) => {
    setSubmitting(false);
  }
})(InnerContactForm);

export default ContactForm;
