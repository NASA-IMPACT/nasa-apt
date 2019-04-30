import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';

import {
  FormGroup,
  FormGroupHeader,
  FormGroupBody
} from '../../styles/form/group';
import FormToolbar from '../../styles/form/toolbar';
import InfoButton from './InfoButton';
import FormLabel from '../../styles/form/label';
import {
  FormHelper,
  FormHelperMessage
} from '../../styles/form/helper';

export const InputFormGroup = styled.form`
  display: grid;
  align-items: start;
  grid-gap: 0.25rem 0.5rem;
  grid-template-columns: repeat(3, 1fr);
  justify-content: space-between;
`;

const InlineInput = styled.input`
  background: #FFF;
  border: 1px solid ${themeVal('color.gray')};
  border-radius: 4px;
  font-family: inherit;
  height: ${multiply(themeVal('layout.space'), 2.4)}
  width: 100%;
`;

export const InputSubmit = styled(InlineInput)`
  box-shadow: ${themeVal('boxShadow.input')};
  font-weight: bold;
  grid-row-start: 4;
`;

export const SmallTextInput = styled(InlineInput)`
`;

const Input = (props) => {
  const {
    error,
    touched,
    label,
    name,
    info,
    id,
    ...inputProps
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  return (
    <FormGroup>
      <FormGroupHeader>
        <FormLabel htmlFor={id}>{label}</FormLabel>
        {info && (
        <FormToolbar>
          <InfoButton text={info} />
        </FormToolbar>
        )}
      </FormGroupHeader>
      <FormGroupBody>
        <SmallTextInput
          id={id}
          name={name}
          {...inputProps}
        />
        {feedback && (
          <FormHelper>
            <FormHelperMessage>
              {feedback}
            </FormHelperMessage>
          </FormHelper>
        )}
      </FormGroupBody>
    </FormGroup>
  );
};

Input.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool,
  info: PropTypes.string,
  id: PropTypes.string
};

export default Input;
