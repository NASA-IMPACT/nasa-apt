import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import {
  createAtbdVersion,
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable
} from '../actions/actions';
import FreeEditor from './FreeEditor';
import AlgorithmVariables from './AlgorithmVariables';
import AlgorithmVariableForm from './AlgorithmVariableForm';
import EditPage from './common/EditPage';

const AlgorithmDescription = (props) => {
  const {
    atbdVersion = {},
    save,
    createAlgorithmInputVariable: createInputVariable,
    createAlgorithmOutputVariable: createOutputVariable
  } = props;

  const {
    atbd_id,
    atbd_version,
    scientific_theory = {},
    algorithm_input_variables = [],
    algorithm_output_variables = []
  } = atbdVersion;

  return (
    <EditPage title="Document title">
      <span>Algorithm Description</span>
      <br />
      <span>Scientifc Theory</span>
      <br />
      <FreeEditor
        value={Value.fromJSON(scientific_theory)}
        save={(document) => {
          save({
            scientific_theory: document
          });
        }}
      />
      <br />
      <span>Scientifc Theory Assumptions</span>
      <br />
      <span>Algorithm Input Variables</span>
      <AlgorithmVariables
        schemaKey="algorithm_input_variable"
        variables={algorithm_input_variables}
      />
      {atbd_id && atbd_version && (
      <AlgorithmVariableForm
        schemaKey="algorithm_input_variable"
        atbd_id={atbd_id}
        atbd_version={atbd_version}
        create={(data) => { createInputVariable(data); }}
      />
      )
      }
      <span>Algorithm Output Variables</span>
      <AlgorithmVariables
        schemaKey="algorithm_output_variable"
        variables={algorithm_output_variables}
      />
      {atbd_id && atbd_version && (
      <AlgorithmVariableForm
        schemaKey="algorithm_output_variable"
        atbd_id={atbd_id}
        atbd_version={atbd_version}
        create={(data) => { createOutputVariable(data); }}
      />
      )
      }
    </EditPage>
  );
};

AlgorithmDescription.propTypes = {
  atbdVersion: PropTypes.object,
  save: PropTypes.func.isRequired,
  createAlgorithmInputVariable: PropTypes.func.isRequired,
  createAlgorithmOutputVariable: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { atbdVersion } = state.application;
  return { atbdVersion };
};

const mapDispatchToProps = {
  createAtbdVersion,
  updateAtbdVersion,
  createAlgorithmInputVariable,
  createAlgorithmOutputVariable
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
