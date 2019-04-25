import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  createAlgorithmImplementation,
  updateAlgorithmImplementation,
  deleteAlgorithmImplementation
} from '../actions/actions';
import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';
import AlgorithmImplementationForm from './AlgorithmImplementationForm';

export function AlgorithmImplementation(props) {
  const {
    atbdVersion,
    atbd,
    createAlgorithmImplementation: create,
    updateAlgorithmImplementation: update,
    deleteAlgorithmImplementation: del
  } = props;
  let returnValue;
  if (atbdVersion && Array.isArray(atbdVersion.algorithm_implementations)) {
    const {
      title,
      atbd_id
    } = atbd;
    const {
      algorithm_implementations,
      atbd_version
    } = atbdVersion;

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={atbd_id}
          step={6}
        >
          <h2>Algorithm Implementation</h2>

          {algorithm_implementations.map((d, i) => (
            <AlgorithmImplementationForm
              key={`algorithm-implementation-form-${i}`} // eslint-disable-line react/no-array-index-key
              id={`algorithm-implementation-form-${i}`}
              label={`Implementation #${i + 1}`}
              accessUrl={d.access_url}
              executionDescription={d.execution_description}
              save={(object) => {
                update(d.algorithm_implementation_id, {
                  access_url: object.accessUrl,
                  execution_description: object.executionDescription
                });
              }}
              del={() => del(d.algorithm_implementation_id)}
            />
          ))}

          <AlgorithmImplementationForm
            id="algorithm-implementation-form-new"
            label="New Implementation"
            save={(object) => {
              create({
                atbd_id,
                atbd_version,
                access_url: object.accessUrl,
                execution_description: object.executionDescription
              });
            }}
          />
        </EditPage>
      </Inpage>
    );
  } else {
    returnValue = <div>Loading</div>;
  }
  return returnValue;
}

AlgorithmImplementation.propTypes = {
  atbdVersion: PropTypes.object,
  atbd: PropTypes.object,
  createAlgorithmImplementation: PropTypes.func,
  updateAlgorithmImplementation: PropTypes.func,
  deleteAlgorithmImplementation: PropTypes.func
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const { atbdVersion } = app;
  const atbd = atbdVersion ? atbdVersion.atbd : {};
  return {
    atbdVersion,
    atbd
  };
};

const mapDispatchToProps = {
  createAlgorithmImplementation,
  updateAlgorithmImplementation,
  deleteAlgorithmImplementation
};

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmImplementation);
