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
import InfoButton from './common/InfoButton';
import Form from '../styles/form/form';
import FormToolbar from '../styles/form/toolbar';
import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
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
    deleteAlgorithmOutputVariable: deleteOutputVariable,
    t
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
          <Form>
            <FormFieldset>
              <FormFieldsetHeader>
                <FormLegend>Algorithm</FormLegend>
              </FormFieldsetHeader>
              <FormFieldsetBody>
                <FormGroup>
                  <FormGroupHeader>
                    <FormLabel>Describe the scientific theory</FormLabel>
                    <FormToolbar>
                      <InfoButton text={t.scientific_theory} />
                    </FormToolbar>
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
              </FormFieldsetBody>
            </FormFieldset>
          </Form>

          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Scientific Theory Assumptions</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <FormGroup>
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
                    t={{
                      name: t.input_variable_name,
                      long_name: t.input_variable_long_name,
                      unit: t.input_variable_unit
                    }}
                  />
                )}
              </FormGroup>

              <FormGroup>
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
                    t={{
                      name: t.output_variable_name,
                      long_name: t.output_variable_long_name,
                      unit: t.output_variable_unit
                    }}
                  />
                )}

              </FormGroup>
            </FormFieldsetBody>
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
  deleteAlgorithmOutputVariable: PropTypes.func.isRequired,
  t: PropTypes.object
};

const mapStateToProps = (state) => {
  const { atbdVersion, t } = state.application;
  return {
    atbdVersion,
    t: t ? t.algorithm_description : {}
  };
};

const mapDispatchToProps = {
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable,
  deleteAlgorithmInputVariable,
  deleteAlgorithmOutputVariable
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmDescription);
