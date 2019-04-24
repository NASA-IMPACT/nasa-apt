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
import {
  Inpage
} from './common/Inpage';
import EditPage, {
  EditorSection,
  EditorSectionTitle,
  EditorLabel
} from './common/EditPage';

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
          <EditorSection>
            <EditorLabel>Scientific Theory</EditorLabel>
            <FreeEditor
              initialValue={scientific_theory}
              save={(document) => {
                update(atbd_id, atbd_version, {
                  scientific_theory: document
                });
              }}
            />
          </EditorSection>
          <EditorSection>
            <EditorLabel>Scientific Theory Assumptions</EditorLabel>
            <EditorSectionTitle>Algorithm Input Variables</EditorSectionTitle>
            <AlgorithmVariables
              schemaKey="algorithm_input_variable"
              variables={algorithm_input_variables}
              deleteVariable={deleteInputVariable}
            />
            {atbd_id && atbd_version && (
              <AlgorithmVariableForm
                schemaKey="algorithm_input_variable"
                atbd_id={atbd_id}
                atbd_version={atbd_version}
                create={(data) => { createInputVariable(data); }}
              />
            )}
          </EditorSection>

          <EditorSection>
            <EditorSectionTitle>Algorithm Output Variables</EditorSectionTitle>
            <AlgorithmVariables
              schemaKey="algorithm_output_variable"
              variables={algorithm_output_variables}
              deleteVariable={deleteOutputVariable}
            />
            {atbd_id && atbd_version && (
              <AlgorithmVariableForm
                schemaKey="algorithm_output_variable"
                atbd_id={atbd_id}
                atbd_version={atbd_version}
                create={(data) => { createOutputVariable(data); }}
              />
            )}
          </EditorSection>
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
