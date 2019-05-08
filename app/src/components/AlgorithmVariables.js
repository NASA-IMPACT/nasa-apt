import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';

import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
} from '../styles/form/fieldset';
import {
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import FormLegend from '../styles/form/legend';
import RemoveButton from '../styles/button/remove';
import { InputFormGroup } from './common/Input';

const VariableList = styled.ul`
  list-style: none;
  margin: 1rem 0;
`;

const VariableListItem = styled.li`
  margin-bottom: 1rem;
  &&:last-child {
    margin-bottom: 0;
  }
`;

const InputProperty = styled.div`
`;

const AlgorithmVariables = (props) => {
  const {
    schemaKey,
    variables,
    deleteVariable
  } = props;

  if (!variables.length) {
    return (
      <FormFieldset>
        <FormFieldsetBody>
          <FormHelper>
            <FormHelperMessage>No variables. Add one below.</FormHelperMessage>
          </FormHelper>
        </FormFieldsetBody>
      </FormFieldset>
    );
  }

  const variableItems = variables.map((variable, i) => {
    const {
      [`${schemaKey}_id`]: id,
      name,
      long_name,
      unit
    } = variable;

    return (
      <VariableListItem key={id}>
        <FormFieldset>
          <FormFieldsetHeader>
            <FormLegend>Variable #{i + 1}</FormLegend>
            <RemoveButton
              variation="base-plain"
              size="small"
              hideText
              onClick={() => deleteVariable(id)}
            >
              Remove
            </RemoveButton>
          </FormFieldsetHeader>
          <FormFieldsetBody>
            <InputFormGroup>
              <InputProperty>
                <strong>Name:</strong> {name}
              </InputProperty>
              <InputProperty>
                <strong>Long Name:</strong> {long_name}
              </InputProperty>
              <InputProperty>
                <strong>Unit:</strong> {unit}
              </InputProperty>
            </InputFormGroup>
          </FormFieldsetBody>
        </FormFieldset>
      </VariableListItem>
    );
  });

  return (
    <VariableList>
      {variableItems}
    </VariableList>
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
