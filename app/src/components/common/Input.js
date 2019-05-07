import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';

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
  width: 100%;
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
