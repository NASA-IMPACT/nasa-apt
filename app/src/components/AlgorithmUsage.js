import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { updateAtbdVersion } from '../actions/actions';

import FreeEditor from './FreeEditor';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import {
  FormFieldset,
  FormFieldsetHeader
} from '../styles/form/fieldset';
import FormLegend from '../styles/form/legend';
import FormLabel from '../styles/form/label';

export function AlgorithmUsage(props) {
  const {
    atbd,
    atbd_version,
    methods,
    uncertainties,
    errors,
    constraints,
    updateAtbdVersion: update
  } = props;

  const {
    atbd_id,
    title
  } = atbd;

  return (
    <Inpage>
      <EditPage
        title={title || ''}
        id={atbd_id}
        step={5}
        numSteps={7}
      >
        <h2>Algorithm Usage</h2>
        <FormFieldset>
          <FormGroup>
            <FormFieldsetHeader>
              <FormLegend>Constraints</FormLegend>
            </FormFieldsetHeader>
            <FormGroupHeader>
              <FormLabel>Describe the algorithm constraints</FormLabel>
            </FormGroupHeader>
            <FormGroupBody>
              <FreeEditor
                initialValue={constraints}
                save={(document) => {
                  update(atbd_id, atbd_version, {
                    algorithm_usage_constraints: document
                  });
                }}
              />
            </FormGroupBody>
          </FormGroup>
        </FormFieldset>

        <h2>Performance Assessment</h2>
        <FormFieldset>
          <FormGroup>
            <FormFieldsetHeader>
              <FormLegend>Validation</FormLegend>
            </FormFieldsetHeader>
            <FormGroupHeader>
              <FormLabel>Validation methods</FormLabel>
            </FormGroupHeader>
            <FormGroupBody>
              <FreeEditor
                initialValue={methods}
                save={(document) => {
                  update(atbd_id, atbd_version, {
                    performance_assessment_validation_methods: document
                  });
                }}
              />
            </FormGroupBody>

            <FormGroupHeader>
              <FormLabel>Uncertainties</FormLabel>
            </FormGroupHeader>
            <FormGroupBody>
              <FreeEditor
                initialValue={uncertainties}
                save={(document) => {
                  update(atbd_id, atbd_version, {
                    performance_assessment_validation_uncertainties: document
                  });
                }}
              />
            </FormGroupBody>

            <FormGroupHeader>
              <FormLabel>Errors</FormLabel>
            </FormGroupHeader>
            <FormGroupBody>
              <FreeEditor
                initialValue={errors}
                save={(document) => {
                  update(atbd_id, atbd_version, {
                    performance_assessment_validation_errors: document
                  });
                }}
              />
            </FormGroupBody>
          </FormGroup>
        </FormFieldset>
      </EditPage>
    </Inpage>
  );
}

AlgorithmUsage.propTypes = {
  atbd: PropTypes.object,
  atbd_version: PropTypes.number,
  methods: PropTypes.object,
  uncertainties: PropTypes.object,
  errors: PropTypes.object,
  constraints: PropTypes.object,
  updateAtbdVersion: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const atbdVersion = app.atbdVersion || {};
  const atbd = atbdVersion.atbd || {};
  return {
    atbd,
    atbd_version: atbdVersion.atbd_version,
    methods: atbdVersion.performance_assessment_validation_methods,
    uncertainties: atbdVersion.performance_assessment_validation_uncertainties,
    errors: atbdVersion.performance_assessment_validation_errors,
    constraints: atbdVersion.algorithm_usage_constraints
  };
};

const mapDispatchToProps = { updateAtbdVersion };

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
