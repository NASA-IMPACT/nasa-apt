import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import collecticon from '../styles/collecticons';

const RemovableListItem = styled.li`
  &::before {
    cursor: pointer;
    ${collecticon('xmark--small')}
  }
`;

const AlgorithmVariables = (props) => {
  const {
    schemaKey,
    variables
  } = props;

  const variableItems = variables.map((variable) => {
    const {
      [`${schemaKey}_id`]: id,
      name,
      long_name,
      unit
    } = variable;

    return (
      <RemovableListItem key={id}>
        {`${name} ${long_name} ${unit}`}
      </RemovableListItem>
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
  }))
};

export default AlgorithmVariables;
