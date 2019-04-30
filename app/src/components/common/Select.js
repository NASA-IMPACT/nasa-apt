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
    id
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  const activeValue = options.find(d => d.value === value);

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
        <ReactSelect
          options={options}
          name={name}
          value={activeValue}
          onChange={e => onChange && onChange({ target: { name, value: e.value } })}
          onBlur={() => onBlur && onBlur(({ target: { name } }))}
          id={id}
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
  error: PropTypes.string,
  touched: PropTypes.bool,
  value: PropTypes.string,
  onChange: PropTypes.func,
  onBlur: PropTypes.func,
  info: PropTypes.string,
  id: PropTypes.string
};
export default Select;
