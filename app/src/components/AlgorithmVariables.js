import React, { Fragment } from 'react';
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

export default AlgorithmVariables;
