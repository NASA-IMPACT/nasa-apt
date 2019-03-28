import React, { Fragment } from 'react';
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
    <Fragment>
      <InputLabel>
        {label}
        <InputLabelFeedback>{feedback}</InputLabelFeedback>
        <SmallTextInput
          id={name}
          name={name}
          {...inputProps}
        />
      </InputLabel>
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
