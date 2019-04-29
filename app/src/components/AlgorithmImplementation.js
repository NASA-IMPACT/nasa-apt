import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import uuid from 'uuid';
import styled from 'styled-components';

import {
  createAlgorithmImplementation,
  updateAlgorithmImplementation,
  deleteAlgorithmImplementation
} from '../actions/actions';
import {
  Inpage
} from './common/Inpage';
import EditPage from './common/EditPage';
import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';
import AlgorithmImplementationForm from './AlgorithmImplementationForm';

const AddBtn = styled(Button)`
  ::before {
    ${collecticon('plus')}
  }
`;

export class AlgorithmImplementation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      implementations: []
    };
    this.addImplementation = this.addImplementation.bind(this);
    this.removeImplementation = this.removeImplementation.bind(this);
  }

  addImplementation() {
    const { implementations } = this.state;
    const next = implementations.concat([uuid()]);
    this.setState({ implementations: next });
  }

  removeImplementation(id) {
    const { implementations } = this.state;
    const next = implementations.filter(d => d !== id);
    this.setState({ implementations: next });
  }

  render() {
    const {
      atbdVersion,
      atbd,
      createAlgorithmImplementation: create,
      updateAlgorithmImplementation: update,
      deleteAlgorithmImplementation: del
    } = this.props;
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
      const { implementations } = this.state;
      const {
        addImplementation,
        removeImplementation
      } = this;

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

            {implementations.map(id => (
              <AlgorithmImplementationForm
                key={id}
                id={id}
                label="New Implementation"
                save={(object) => {
                  create({
                    atbd_id,
                    atbd_version,
                    access_url: object.accessUrl,
                    execution_description: object.executionDescription
                  });
                  removeImplementation(id);
                }}
                del={() => removeImplementation(id)}
              />
            ))}

            <AddBtn
              variation="base-plain"
              onClick={addImplementation}
            >
              Add an implementation
            </AddBtn>

          </EditPage>
        </Inpage>
      );
    } else {
      returnValue = <div>Loading</div>;
    }
    return returnValue;
  }
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
