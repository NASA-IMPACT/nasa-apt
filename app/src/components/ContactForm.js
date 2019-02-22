/* eslint camel-case: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import apiSchema from '../schemas/schema.json';
import addMinLength from '../schemas/addMinLength';
import transformErrors from '../schemas/transformErrors';

const validator = new jsonschema.Validator();
const contactsSchema = addMinLength(apiSchema.definitions.contacts);

const InnerContactForm = (props) => {
  const name = 'first_name';
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
      <input
        name={name}
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[name]}
      />
      {errors[name] && touched[name] && <div id="feedback">{errors[name]}</div>}
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
      first_name: ''
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
