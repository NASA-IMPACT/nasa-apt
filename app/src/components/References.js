import React from 'react';
import { PropTypes as T } from 'prop-types';
import { connect } from 'react-redux';
import { deleteReference } from '../actions/actions';

import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';
import RemoveButton from '../styles/button/remove';

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
          <p>
            Please remove any references that are no longer attached to this ATBD.<br />
            Do not delete any that are currently referenced in any section with a <sup>ref</sup> superscript.
          </p>
          <ul>
            {references.map((d, i) => (
              <li key={d.publication_reference_id}>
                <span>#{i + 1} {d.title}</span>
                <RemoveButton
                  variation="base-plain"
                  size="small"
                  hideText
                  onClick={() => del(d.publication_reference_id)}
                >
                  Delete
                </RemoveButton>
              </li>
            ))}
            {!references.length && <p>No references attached.</p>}
          </ul>
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
