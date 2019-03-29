import React from 'react';
import PropTypes from 'prop-types';
import {
  InputLabel,
  SmallTextInput,
  InputLabelFeedback
} from './common/EditPage';

const Input = (props) => {
  const {
    error,
    touched,
    label,
    name,
    ...inputProps
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  return (
    <InputLabel>
      {label}
      <InputLabelFeedback>{feedback}</InputLabelFeedback>
      <SmallTextInput
        id={name}
        name={name}
        {...inputProps}
      />
    </InputLabel>
  );
};

Input.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool
};

export default Input;
