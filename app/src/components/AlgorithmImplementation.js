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

export function AlgorithmImplementation(props) {
  return (
    <Inpage>
      <EditPage
        title={''}
        id={1}
        step={6}
      >
        <h2>Algorithm Implementation</h2>
      </EditPage>
    </Inpage>
  );
}

const mapStateToProps = (state) => {
  return {};
};

const mapDispatchToProps = {};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmImplementation);
