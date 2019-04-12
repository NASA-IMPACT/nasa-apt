import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import {
  createAtbdVersion,
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
import editorBlankDocument from './editorBlankDocument';

export const AlgorithmDescription = (props) => {
  const {
    atbdVersion = {},
    save,
    createAlgorithmInputVariable: createInputVariable,
    createAlgorithmOutputVariable: createOutputVariable,
    deleteAlgorithmInputVariable: deleteInputVariable,
    deleteAlgorithmOutputVariable: deleteOutputVariable
  } = props;

  const {
    atbd,
    atbd_id,
    atbd_version,
    scientific_theory = editorBlankDocument,
    algorithm_input_variables = [],
    algorithm_output_variables = []
  } = atbdVersion;

  const title = atbd && atbd.title;

  return (
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
            value={Value.fromJSON(scientific_theory)}
            save={(document) => {
              save({
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
};

AlgorithmDescription.propTypes = {
  atbdVersion: PropTypes.object,
  save: PropTypes.func.isRequired,
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
  createAtbdVersion,
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable,
  deleteAlgorithmInputVariable,
  deleteAlgorithmOutputVariable
};

const mergeProps = (stateProps, dispatchProps) => {
  const { atbdVersion } = stateProps;
  const {
    createAtbdVersion: create,
    updateAtbdVersion: update
  } = dispatchProps;
  let save;
  if (atbdVersion) {
    const { atbd_id, atbd_version } = atbdVersion;
    save = (value) => {
      update(atbd_id, atbd_version, value);
    };
  } else {
    save = (value) => {
      create(value);
    };
  }
  return {
    ...stateProps,
    ...dispatchProps,
    save
  };
};

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(AlgorithmDescription);
