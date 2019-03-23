import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import { createAlgorithmDescription } from '../actions/actions';
import FreeEditor from './FreeEditor';

const AlgorithmDescription = (props) => {
  const {
    algorithmDescription = {},
    save
  } = props;
  console.log(algorithmDescription);
  const { scientific_theory = {} } = algorithmDescription;
  return (
    <FreeEditor
      value={Value.fromJSON(scientific_theory)}
      save={(document) => {
        save({
          ...algorithmDescription,
          scientific_theory: document
        });
      }}
    />
  );
};
const mapStateToProps = (state) => {
  const { algorithmDescription } = state.application;
  return { algorithmDescription };
};

//const mapDispatchToProps = dispatch => ({
  //createDocument: document => dispatch(createAlgorithmDescription(document)),
//});

const mapDispatchToProps = {
  createAlgorithmDescription
};

const mergeProps = (stateProps, dispatchProps) => {
  const { algorithmDescription } = stateProps;
  const { createAlgorithmDescription: create } = dispatchProps;
  let save;
  if (algorithmDescription) {
    save = (value) => {
      console.log(value);
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
