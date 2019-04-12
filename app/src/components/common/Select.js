import React from 'react';
import ReactSelect from 'react-select';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import ReactTooltip from 'react-tooltip';
import collecticon from '../../styles/collecticons';

import FormGroup from '../../styles/form/group';
import FormToolbar from '../../styles/form/toolbar';
import FormLabel from '../../styles/form/label';
import FormHelp from '../../styles/form/help';
import Button from '../../styles/button/button';

const InfoButton = styled(Button)`
  &::before {
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
      <FormLabel htmlFor={id}>{label}</FormLabel>
      {info && (
        <FormToolbar>
          <InfoButton
            variation="base-plain"
            size="small"
            hideText
            data-tip={info}
          >
            Learn more
          </InfoButton>
          <ReactTooltip effect="solid" className="type-primary" />
        </FormToolbar>
      )}
      <ReactSelect
        options={options}
        name={name}
        value={activeValue}
        onChange={e => onChange && onChange({ target: { name, value: e.value } })}
        onBlur={() => onBlur && onBlur(({ target: { name } }))}
        id={id}
      />
      {feedback && (
        <FormHelp>{feedback}</FormHelp>
      )}
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
