import React from 'react';
import { PropTypes as T } from 'prop-types';
import { connect } from 'react-redux';
import { deleteReference } from '../actions/actions';
import RemovableListItem from './common/RemovableListItem';

import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';

export function References(props) {
  const {
    atbdVersion,
    references,
    deleteReference: del
  } = props;
  let returnValue;
  if (atbdVersion) {
    const {
      atbd,
      atbd_id
    } = atbdVersion;
    const { title } = atbd;
    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={7}
        >
          <h2>References</h2>
          {references.map(d => (
            <RemovableListItem
              key={d.publication_reference_id}
              label={d.title}
              deleteAction={() => del(d.publication_reference_id)}
            />
          ))}
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = null;
  }
  return returnValue;
}

References.propTypes = {
  atbdVersion: T.object,
  references: T.array,
  deleteReference: T.func
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion,
  references: state.application.references
});

const mapDispatch = { deleteReference };

export default connect(mapStateToProps, mapDispatch)(References);
