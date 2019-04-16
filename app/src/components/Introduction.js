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
  EditorSectionTitle
} from './common/EditPage';
import editorBlankDocument from './editorBlankDocument';

export function Introduction (props) {
  const {
    atbdVersion = {},
    update
  } = props;

  const {
    atbd,
    atbd_id,
    atbd_version,
    introduction = editorBlankDocument
  } = atbdVersion;

  const title = atbd && atbd.title;

  return (
    <Inpage>
      <EditPage
        title={title || ''}
        id={atbd_id}
        step={2}
        numSteps={7}
      >
        <h2>Introduction</h2>
        <EditorSection>
          <FreeEditor
            value={Value.fromJSON(introduction)}
            save={(document) => {
              console.log('save', document);
              update(atbd_id, atbd_version, {
                introduction: document
              })
            }}
          />
        </EditorSection>
      </EditPage>
    </Inpage>
  );
}

Introduction.propTypes = {
  atbdVersion: PropTypes.object
};

const mapStateToProps = (state) => ({
  atbdVersion: state.application.atbdVersion
});

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(Introduction);
