import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { multiply } from '../styles/utils/math';
import collecticon from '../styles/collecticons';
import { themeVal } from '../styles/utils/general';

const DeleteIcon = styled('span')`
  cursor: pointer ;
  &:hover {
    color: ${themeVal('color.danger')}
  }
  &::before {
    margin-left: ${multiply(themeVal('layout.space'), 0.5)};
    vertical-align: middle;
    ${collecticon('trash-bin')}
  }
`;

const Variable = styled('span')`
  vertical-align: middle;
`;

const AlgorithmVariables = (props) => {
  const {
    schemaKey,
    variables,
    deleteVariable
  } = props;

  const variableItems = variables.map((variable) => {
    const {
      [`${schemaKey}_id`]: id,
      name,
      long_name,
      unit
    } = variable;

    return (
      <li key={id}>
        <Variable>{`${name} ${long_name} ${unit}`}</Variable>
        <DeleteIcon onClick={() => deleteVariable(id)} />
      </li>
    );
  });

  return (
    <ul>
      {variableItems}
    </ul>
  );
};

AlgorithmVariables.propTypes = {
  schemaKey: PropTypes.string.isRequired,
  variables: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    long_name: PropTypes.string,
    unit: PropTypes.string
  })),
  deleteVariable: PropTypes.func.isRequired
};

export default AlgorithmVariables;
