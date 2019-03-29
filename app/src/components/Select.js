import React from 'react';
import PropTypes from 'prop-types';
import {
  InputLabel,
  InputLabelFeedback
} from './common/EditPage';

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
    <InputLabel>
      {label}
      <InputLabelFeedback>{feedback}</InputLabelFeedback>
      <select
        id={name}
        name={name}
        {...inputProps}
      >
        {optionElements}
      </select>
    </InputLabel>
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
