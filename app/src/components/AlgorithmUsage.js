import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import { get } from 'object-path';
import {
  savePerformanceAssessmentMethods,
  savePerformanceAssessmentUncertainties,
  savePerformanceAssessmentErrors
} from '../actions/actions';

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
    saveMethods,
    saveUncertainties,
    saveErrors
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
            value={Value.fromJSON(getValidOrBlankDocument(null))}
            save={() => true}
          />
        </EditorSection>

        <h2>Performance Assessment</h2>
        <EditorSection>
          <EditorLabel>Validation methods</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(methods.description))}
            save={(document) => {
              saveMethods({
                id: methods.performance_assessment_validation_method_id,
                atbd_id,
                atbd_version,
                description: document
              });
            }}
          />

          <EditorLabel>Validation uncertainties</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(uncertainties.description))}
            save={(document) => {
              saveUncertainties({
                id: uncertainties.performance_assessment_validation_uncertainty,
                atbd_id,
                atbd_version,
                description: document
              });
            }}
          />

          <EditorLabel>Validation errors</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(errors.description))}
            save={(document) => {
              saveErrors({
                id: errors.performance_assessment_validation_error,
                atbd_id,
                atbd_version,
                description: document
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
  saveMethods: PropTypes.func,
  saveUncertainties: PropTypes.func,
  saveErrors: PropTypes.func
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  return {
    atbd: get(app, 'atbdVersion.atbd', {}),
    atbd_version: get(app, 'atbdVersion.atbd_version'),
    methods: get(app.performanceAssessment, 'methods', {}),
    uncertainties: get(app.performanceAssessment, 'uncertainties', {}),
    errors: get(app.performanceAssessment, 'errors', {})
  };
};

const mapDispatchToProps = {
  saveMethods: savePerformanceAssessmentMethods,
  saveUncertainties: savePerformanceAssessmentUncertainties,
  saveErrors: savePerformanceAssessmentErrors
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
