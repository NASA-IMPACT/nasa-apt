import React from 'react';
import ReactSelect from 'react-select';
import PropTypes from 'prop-types';

import {
  FormGroup,
  FormGroupHeader,
  FormGroupBody
} from '../../styles/form/group';
import FormToolbar from '../../styles/form/toolbar';
import FormLabel from '../../styles/form/label';
import {
  FormHelper,
  FormHelperMessage
} from '../../styles/form/helper';
import InfoButton from './InfoButton';

const Select = (props) => {
  const {
    error,
    touched,
    label,
    name,
    options,
    value,
    onChange,
    onBlur,
    info,
    id,
    readonly,
    optional
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  const activeValue = options.find(d => d.value === value);

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
        <ReactSelect
          options={options}
          name={name}
          value={activeValue}
          onChange={onChange}
          onBlur={() => onBlur && onBlur(({ target: { name } }))}
          id={id}
          isDisabled={readonly}
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

Select.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  options: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
  touched: PropTypes.bool,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number
  ]),
  onBlur: PropTypes.func,
  info: PropTypes.string,
  id: PropTypes.string,
  readonly: PropTypes.bool,
  optional: PropTypes.bool
};
export default Select;
