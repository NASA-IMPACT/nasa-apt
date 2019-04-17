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
import editorBlankDocument from './editorBlankDocument';

export function AlgorithmUsage(props) {
  return (
    <Inpage>
      <EditPage
        title={''}
        id={12}
        step={2}
        numSteps={7}
      >
        <h2>Algorithm Usage</h2>
      </EditPage>
    </Inpage>
  );
}

AlgorithmUsage.propTypes = {
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion
});

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
