import React, { Fragment } from 'react';
import PropTypes from 'prop-types';

const Select = (props) => {
  const {
    error,
    touched,
    label,
    name,
    options,
    ...inputProps
  } = props;

  let feedback = <div />;
  if (Boolean(error) && touched) {
    feedback = <div>{error}</div>;
  }

  const optionElements = options.map(option => (
    <option
      key={option}
      value={option}
    >
      {option}
    </option>
  ));

  return (
    <Fragment>
      <label htmlFor={name}>{label}</label>
      <select
        id={name}
        name={name}
        {...inputProps}
      >
        {optionElements}
      </select>
      {feedback}
    </Fragment>
  );
};

Select.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  options: PropTypes.array.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool
};
export default Select;
