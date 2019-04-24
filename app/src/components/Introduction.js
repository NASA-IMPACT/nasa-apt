import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { updateAtbdVersion } from '../actions/actions';

import FreeEditor from './FreeEditor';
import {
  Inpage
} from './common/Inpage';
import EditPage, {
  EditorSection,
  EditorLabel
} from './common/EditPage';

export function Introduction(props) {
  const {
    atbdVersion = {},
    update
  } = props;

  const {
    atbd,
    atbd_id,
    atbd_version,
    historical_perspective,
    introduction
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
          <EditorLabel>Introduction</EditorLabel>
          <FreeEditor
            initialValue={introduction}
            save={(document) => {
              update(atbd_id, atbd_version, {
                introduction: document
              });
            }}
          />
        </EditorSection>
        <EditorSection>
          <EditorLabel>Historical Perspective</EditorLabel>
          <FreeEditor
            initialValue={historical_perspective}
            save={(document) => {
              update(atbd_id, atbd_version, {
                historical_perspective: document
              });
            }}
          />
        </EditorSection>
      </EditPage>
    </Inpage>
  );
}

Introduction.propTypes = {
  atbdVersion: PropTypes.object,
  update: PropTypes.func
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion
});

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(Introduction);
