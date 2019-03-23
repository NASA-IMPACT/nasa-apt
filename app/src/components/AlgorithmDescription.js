import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import {
  createAtbdVersion,
  updateAtbdVersion
} from '../actions/actions';
import FreeEditor from './FreeEditor';

const AlgorithmDescription = (props) => {
  const {
    atbdVersion = {},
    save
  } = props;

  const { scientific_theory = {} } = atbdVersion;

  return (
    <Fragment>
      <span>Scientifc Theory</span>
      <br />
      <FreeEditor
        value={Value.fromJSON(scientific_theory)}
        save={(document) => {
          save({
            scientific_theory: document
          });
        }}
      />
    </Fragment>
  );
};

AlgorithmDescription.propTypes = {
  atbdVersion: PropTypes.object,
  save: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { atbdVersion } = state.application;
  return { atbdVersion };
};

const mapDispatchToProps = {
  createAtbdVersion,
  updateAtbdVersion
};

const mergeProps = (stateProps, dispatchProps) => {
  const { atbdVersion } = stateProps;
  const {
    createAtbdVersion: create,
    updateAtbdVersion: update
  } = dispatchProps;
  let save;
  if (atbdVersion) {
    const { atbd_id, atbd_version } = atbdVersion;
    save = (value) => {
      update(atbd_id, atbd_version, value);
    };
  } else {
    save = (value) => {
      create(value);
    };
  }
  return {
    ...stateProps,
    save
  };
};

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(AlgorithmDescription);
