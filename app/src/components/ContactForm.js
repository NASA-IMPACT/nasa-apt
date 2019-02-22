/* eslint camelcase: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';
import Input from './Input';

const validator = new jsonschema.Validator();
const contactsSchema = addMinLength(apiSchema.definitions.contacts);
const first_name = 'first_name';
const middle_name = 'middle_name';

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
      [middle_name]: ''
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
