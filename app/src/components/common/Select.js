import React from 'react';
import ReactSelect from 'react-select';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import ReactTooltip from 'react-tooltip';
import collecticon from '../../styles/collecticons';

import FormGroup from '../../styles/molecules/form/group';
import FormToolbar from '../../styles/molecules/form/toolbar';
import FormLabel from '../../styles/atoms/form/label';
import FormHelp from '../../styles/atoms/form/help';
import Button from '../../styles/atoms/button';

const InfoButton = styled(Button)`
  ::before {
    ${collecticon('circle-information')}
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
    <FormGroup>
      <FormLabel>{label}</FormLabel>
      <FormToolbar>
        <InfoButton
          variation="base-plain"
          size="small"
          hideText
          data-tip="Lorem ipsum dolor sit amet."
        >
          Learn more
        </InfoButton>
        <ReactTooltip effect="solid" className="type-primary" />
      </FormToolbar>
      <ReactSelect
        options={options}
        name={name}
        value={activeValue}
        onChange={e => onChange && onChange({ target: { name, value: e.value } })}
        onBlur={() => onBlur && onBlur(({ target: { name } }))}
      />
      <FormHelp>{feedback}</FormHelp>
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
  onBlur: PropTypes.func
};
export default Select;
