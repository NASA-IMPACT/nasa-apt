import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import {
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable,
  deleteAlgorithmInputVariable,
  deleteAlgorithmOutputVariable
} from '../actions/actions';
import FreeEditor from './FreeEditor';
import AlgorithmVariables from './AlgorithmVariables';
import AlgorithmVariableForm from './AlgorithmVariableForm';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import {
  FormFieldset,
  FormFieldsetHeader
} from '../styles/form/fieldset';
import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import FormLabel from '../styles/form/label';
import FormLegend from '../styles/form/legend';

export const AlgorithmDescription = (props) => {
  const {
    atbdVersion,
    updateAtbdVersion: update,
    createAlgorithmInputVariable: createInputVariable,
    createAlgorithmOutputVariable: createOutputVariable,
    deleteAlgorithmInputVariable: deleteInputVariable,
    deleteAlgorithmOutputVariable: deleteOutputVariable
  } = props;

  let returnValue;
  if (atbdVersion) {
    const {
      atbd,
      atbd_id,
      atbd_version,
      algorithm_input_variables = [],
      algorithm_output_variables = []
    } = atbdVersion;

    const { scientific_theory } = atbdVersion;
    const title = atbd && atbd.title;

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={4}
        >
          <h2>Algorithm Description</h2>
          <FormFieldset>
            <FormGroup>
              <FormFieldsetHeader>
                <FormLegend>Algorithm</FormLegend>
              </FormFieldsetHeader>
              <FormGroupHeader>
                <FormLabel>Describe the scientific theory</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <FreeEditor
                  initialValue={scientific_theory}
                  save={(document) => {
                    update(atbd_id, atbd_version, {
                      scientific_theory: document
                    });
                  }}
                />
              </FormGroupBody>
            </FormGroup>
          </FormFieldset>

          <FormFieldset>
            <FormGroup>
              <FormFieldsetHeader>
                <FormLegend>Scientific Theory Assumptions</FormLegend>
              </FormFieldsetHeader>
              <FormGroupHeader>
                <FormLabel>Input variables</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <AlgorithmVariables
                  schemaKey="algorithm_input_variable"
                  variables={algorithm_input_variables}
                  deleteVariable={deleteInputVariable}
                />
              </FormGroupBody>
              {atbd_id && atbd_version && (
                <AlgorithmVariableForm
                  schemaKey="algorithm_input_variable"
                  atbd_id={atbd_id}
                  atbd_version={atbd_version}
                  create={(data) => { createInputVariable(data); }}
                />
              )}

              <FormGroupHeader>
                <FormLabel>Output variables</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <AlgorithmVariables
                  schemaKey="algorithm_output_variable"
                  variables={algorithm_output_variables}
                  deleteVariable={deleteOutputVariable}
                />
              </FormGroupBody>
              {atbd_id && atbd_version && (
                <AlgorithmVariableForm
                  schemaKey="algorithm_output_variable"
                  atbd_id={atbd_id}
                  atbd_version={atbd_version}
                  create={(data) => { createOutputVariable(data); }}
                />
              )}

            </FormGroup>
          </FormFieldset>
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = <div>Loading</div>;
  }
  return returnValue;
};

AlgorithmDescription.propTypes = {
  atbdVersion: PropTypes.object,
  updateAtbdVersion: PropTypes.func.isRequired,
  createAlgorithmInputVariable: PropTypes.func.isRequired,
  createAlgorithmOutputVariable: PropTypes.func.isRequired,
  deleteAlgorithmInputVariable: PropTypes.func.isRequired,
  deleteAlgorithmOutputVariable: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { atbdVersion } = state.application;
  return { atbdVersion };
};

const mapDispatchToProps = {
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable,
  deleteAlgorithmInputVariable,
  deleteAlgorithmOutputVariable
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmDescription);
