import React, { Fragment } from 'react';
import PropTypes from 'prop-types';

const Input = (props) => {
  const {
    error,
    touched,
    label,
    name,
    ...inputProps
  } = props;

  let feedback = <div />;
  if (Boolean(error) && touched) {
    feedback = <div>{error}</div>;
  }
  return (
    <Fragment>
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        {...inputProps}
      />
      {feedback}
    </Fragment>
  );
};

Input.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool
};

export default Input;
