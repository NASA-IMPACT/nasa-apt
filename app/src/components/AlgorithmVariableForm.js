import React from 'react';
import PropTypes from 'prop-types';
import { withFormik } from 'formik';
import jsonschema from 'jsonschema';
import apiSchema from '../schemas/schema.json';
import transformErrors from '../schemas/transformErrors';
import Input, {
  InputFormGroup,
  InputSubmit,
  InputWrapper
} from './common/Input';

const name = 'name';
const long_name = 'long_name';
const unit = 'unit';

const validator = new jsonschema.Validator();

export const InnerAlgorithmVariableForm = (props) => {
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
        name={name}
        label="Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[name]}
        error={errors[name]}
        touched={touched[name]}
      />
      <Input
        name={long_name}
        label="Long Name"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[long_name]}
        error={errors[long_name]}
        touched={touched[long_name]}
      />
      <Input
        name={unit}
        label="Unit"
        type="text"
        onChange={handleChange}
        onBlur={handleBlur}
        value={values[unit]}
        error={errors[unit]}
        touched={touched[unit]}
      />
      <InputWrapper>
        <InputSubmit
          type="submit"
          disabled={!submitEnabled}
          value="Add Algorithm Variable"
        />
      </InputWrapper>
    </InputFormGroup>
  );
};

InnerAlgorithmVariableForm.propTypes = {
  values: PropTypes.object.isRequired,
  touched: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
  handleChange: PropTypes.func.isRequired,
  handleBlur: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired
};

export const AlgorithmVariableForm = withFormik({
  mapPropsToValues: (props) => {
    const { atbd_id, atbd_version } = props;
    const initialValues = {
      atbd_id,
      atbd_version,
      [name]: '',
      [long_name]: '',
      [unit]: '',
    };
    return initialValues;
  },

  validate: (values, props) => {
    let errors = {};
    const { schemaKey } = props;
    const schema = apiSchema.definitions[`${schemaKey}s`];
    schema.required = schema.required.filter(
      property => (property !== `${schemaKey}_id`)
    );
    errors = transformErrors(
      validator.validate(values, schema).errors
    );
    return errors;
  },

  handleSubmit: (values, { props, setSubmitting, resetForm }) => {
    const { create } = props;
    create(values);
    setSubmitting(false);
    resetForm();
  }
})(InnerAlgorithmVariableForm);

AlgorithmVariableForm.propTypes = {
  create: PropTypes.func.isRequired,
  schemaKey: PropTypes.string.isRequired,
  atbd_id: PropTypes.number.isRequired,
  atbd_version: PropTypes.number.isRequired
};

export default AlgorithmVariableForm;
