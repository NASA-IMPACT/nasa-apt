import React from 'react';
import PropTypes from 'prop-types';
import RemovableListItem from './common/RemovableListItem';

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
      <RemovableListItem
        key={id}
        label={`${name} || ${long_name} || ${unit}`}
        deleteAction={() => deleteVariable(id)}
      />
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
