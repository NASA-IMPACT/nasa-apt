import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';
import AlgorithmImplementationForm from './AlgorithmImplementationForm';

export function AlgorithmImplementation(props) {
  const {
    atbdVersion,
    atbd
  } = props;
  let returnValue;
  if (atbdVersion && Array.isArray(atbdVersion.algorithm_implementations)) {
    const {
      title,
      atbd_id
    } = atbd;

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={6}
        >
          <h2>Algorithm Implementation</h2>

          {atbdVersion.algorithm_implementations.map((d, i) => (
            <AlgorithmImplementationForm
              id={`algorithm-implementation-form-${i}`}
              label={`Implementation #${i + 1}`}
              accessUrl={d.access_url}
              executionDescription={d.execution_description}
              save={() => true}
            />
          ))}

          <AlgorithmImplementationForm
            id="algorithm-implementation-form-new"
            label="New Implementation"
            save={(payload) => console.log(payload)}
          />
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = <div>Loading</div>;
  }
  return returnValue;
}

const mapStateToProps = (state) => {
  const { application: app } = state;
  const { atbdVersion } = app;
  const atbd = atbdVersion ? atbdVersion.atbd : {};
  return {
    atbdVersion,
    atbd
  };
};

const mapDispatchToProps = {};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmImplementation);
