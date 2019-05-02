import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';

import Input from '../../styles/form/input';
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

export const InputFormGroup = styled.div`
  display: grid;
  align-items: start;
  grid-gap: 1rem;
  grid-template-columns: repeat(3, 1fr);
  justify-content: space-between;
  margin-bottom: 1rem;
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
  margin-top: 1rem;
  grid-column-start: 1;
`;

const InputForm = (props) => {
  const {
    error,
    touched,
    label,
    name,
    info,
    id,
    optional,
    ...inputProps
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  return (
    <FormGroup>
      <FormGroupHeader>
        <FormLabel htmlFor={id} optional={optional}>{label}</FormLabel>
        {info && (
        <FormToolbar>
          <InfoButton text={info} />
        </FormToolbar>
        )}
      </FormGroupHeader>
      <FormGroupBody>
        <Input
          id={id}
          name={name}
          size="large"
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

InputForm.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool,
  info: PropTypes.string,
  id: PropTypes.string,
  optional: PropTypes.bool
};

export default InputForm;
