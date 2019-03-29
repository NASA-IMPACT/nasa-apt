import React from 'react';
import ReactSelect from 'react-select';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {
  InputLabel,
  InputLabelFeedback
} from './common/EditPage';

const SelectContainer = styled.div`
  > * {
    margin-top: 0.5rem;
  }
`;

const Select = (props) => {
  const {
    error,
    touched,
    label,
    name,
    options,
    value,
    onChange,
    onBlur
  } = props;

  let feedback = null;
  if (Boolean(error) && touched) {
    feedback = error;
  }
  const activeValue = options.find(d => d.value === value);

  return (
    <InputLabel>
      {label}
      <InputLabelFeedback>{feedback}</InputLabelFeedback>
      <SelectContainer>
        <ReactSelect
          options={options}
          name={name}
          value={activeValue}
          onChange={e => onChange && onChange({ target: { name, value: e.value } })}
          onBlur={() => onBlur && onBlur(({ target: { name } }))}
        />
      </SelectContainer>
    </InputLabel>
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
  onBlur: PropTypes.func
};
export default Select;
