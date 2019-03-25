import React from 'react';
import PropTypes from 'prop-types';

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
      <li key={id}>
        {`${name} ${long_name} ${unit}`}
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
  }))
};

export default AlgorithmVariables;
