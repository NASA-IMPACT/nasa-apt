import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';

export const InputLabel = styled.label`
  display: block
  font-weight: bold;
  width: 100%;
`;

export const InputLabelFeedback = styled.span`
  color: ${themeVal('color.danger')};
  font-weight: normal;
  margin-left: ${multiply(themeVal('layout.space'), 0.25)};
`;

export const InputFormGroup = styled.form`
  align-items: end;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 1rem;
  justify-content: space-between;
  margin-top: ${themeVal('layout.space')};
`;

const InlineInput = styled.input`
  background: #FFF;
  border: 1px solid ${themeVal('color.gray')};
  border-radius: 4px;
  font-family: inherit;
  margin: ${multiply(themeVal('layout.space'), 0.5)} 0 0;
  height: ${multiply(themeVal('layout.space'), 2.4)}
  padding: 0 ${multiply(themeVal('layout.space'), 0.5)};
  width: 100%;
`;

export const InputSubmit = styled(InlineInput)`
  box-shadow: ${themeVal('boxShadow.input')};
  font-weight: bold;
`;

export const SmallTextInput = styled(InlineInput)`
`;

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
