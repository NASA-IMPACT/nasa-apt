import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import { get } from 'object-path';
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
    atbd = {},
    methods,
    uncertainties,
    errors,
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
            value={Value.fromJSON(getValidOrBlankDocument(methods))}
            save={() => true}
          />

          <EditorLabel>Validation uncertainties</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(uncertainties))}
            save={() => true}
          />

          <EditorLabel>Validation errors</EditorLabel>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(errors))}
            save={() => true}
          />
        </EditorSection>
      </EditPage>
    </Inpage>
  );
}

AlgorithmUsage.propTypes = {
  atbd: PropTypes.object,
  methods: PropTypes.array,
  uncertainties: PropTypes.array,
  errors: PropTypes.array
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  return {
    atbd: get(app, 'atbdVersion.atbd', {}),
    methods: app.performanceAssessment.methods,
    uncertainties: app.performanceAssessment.uncertainties,
    errors: app.performanceAssessment.errors
  };
};

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
