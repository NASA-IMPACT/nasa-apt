import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import { updateAtbdVersion } from '../actions/actions';

import FreeEditor from './FreeEditor';
import {
  Inpage
} from './common/Inpage';
import EditPage, {
  EditorSection,
  EditorLabel
} from './common/EditPage';
import { getValidOrBlankDocument } from './editorBlankDocument';

export function AlgorithmUsage(props) {
  const {
    atbd,
    atbd_version,
    methods,
    uncertainties,
    errors,
    constraints,
    updateAtbdVersion: update
  } = props;

  const {
    atbd_id,
    title
  } = atbd;

  return (
    <Inpage>
      <EditPage
        title={title || ''}
        id={atbd_id}
        step={5}
        numSteps={7}
      >
        <h2>Algorithm Usage</h2>
        <EditorSection>
          <EditorLabel>Constraints</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(constraints))}
            save={(document) => {
              update(atbd_id, atbd_version, {
                algorithm_usage_constraints: document
              });
            }}
          />
        </EditorSection>

        <h2>Performance Assessment</h2>
        <EditorSection>
          <EditorLabel>Validation methods</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(methods))}
            save={(document) => {
              update(atbd_id, atbd_version, {
                performance_assessment_validation_methods: document
              });
            }}
          />

          <EditorLabel>Validation uncertainties</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(uncertainties))}
            save={(document) => {
              update(atbd_id, atbd_version, {
                performance_assessment_validation_uncertainties: document
              });
            }}
          />

          <EditorLabel>Validation errors</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(errors))}
            save={(document) => {
              update(atbd_id, atbd_version, {
                performance_assessment_validation_errors: document
              });
            }}
          />
        </EditorSection>
      </EditPage>
    </Inpage>
  );
}

AlgorithmUsage.propTypes = {
  atbd: PropTypes.object,
  atbd_version: PropTypes.number,
  methods: PropTypes.object,
  uncertainties: PropTypes.object,
  errors: PropTypes.object,
  constraints: PropTypes.object,
  updateAtbdVersion: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const atbdVersion = app.atbdVersion || {};
  const atbd = atbdVersion.atbd || {};
  return {
    atbd,
    atbd_version: atbdVersion.atbd_version,
    methods: atbdVersion.performance_assessment_validation_methods,
    uncertainties: atbdVersion.performance_assessment_validation_uncertainties,
    errors: atbdVersion.performance_assessment_validation_errors,
    constraints: atbdVersion.algorithm_usage_constraints
  };
};

const mapDispatchToProps = { updateAtbdVersion };

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
