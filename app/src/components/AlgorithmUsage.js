import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { updateAtbdVersion } from '../actions/actions';

import FreeEditor from './FreeEditor';
import { Inpage } from './common/Inpage';
import InfoButton from './common/InfoButton';
import EditPage from './common/EditPage';
import Form from '../styles/form/form';
import FormToolbar from '../styles/form/toolbar';
import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import {
  FormFieldset,
  FormFieldsetHeader,
  FormFieldsetBody
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
    updateAtbdVersion: update,
    t
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
        <Form>
          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Constraints</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <FormGroup>
                <FormGroupHeader>
                  <FormLabel>Describe the algorithm constraints</FormLabel>
                  <FormToolbar>
                    <InfoButton text={t.constraints} />
                  </FormToolbar>
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
            </FormFieldsetBody>
          </FormFieldset>
        </Form>

        <h2>Performance Assessment</h2>
        <Form>
          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Validation</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <FormGroup>
                <FormGroupHeader>
                  <FormLabel>Validation methods</FormLabel>
                  <FormToolbar>
                    <InfoButton text={t.validation_methods} />
                  </FormToolbar>
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
              </FormGroup>
              <FormGroup>
                <FormGroupHeader>
                  <FormLabel>Uncertainties</FormLabel>
                  <FormToolbar>
                    <InfoButton text={t.validation_uncertainties} />
                  </FormToolbar>
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
              </FormGroup>
              <FormGroup>
                <FormGroupHeader>
                  <FormLabel>Errors</FormLabel>
                  <FormToolbar>
                    <InfoButton text={t.validation_errors} />
                  </FormToolbar>
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
            </FormFieldsetBody>
          </FormFieldset>
        </Form>
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
  updateAtbdVersion: PropTypes.func.isRequired,
  t: PropTypes.object
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
    constraints: atbdVersion.algorithm_usage_constraints,
    t: app.t ? app.t.algorithm_usage : {}
  };
};

const mapDispatchToProps = { updateAtbdVersion };

export default connect(mapStateToProps, mapDispatchToProps)(AlgorithmUsage);
