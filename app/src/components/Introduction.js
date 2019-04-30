import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { updateAtbdVersion } from '../actions/actions';

import FreeEditor from './FreeEditor';
import { Inpage } from './common/Inpage';
import EditPage from './common/EditPage';
import InfoButton from './common/InfoButton';
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
import FormLabel from '../styles/form/label';
import FormLegend from '../styles/form/legend';

export function Introduction(props) {
  const {
    atbdVersion = {},
    update,
    t
  } = props;

  const {
    atbd,
    atbd_id,
    atbd_version,
    historical_perspective,
    introduction
  } = atbdVersion;

  const title = atbd && atbd.title;

  return (
    <Inpage>
      <EditPage
        title={title || ''}
        id={atbd_id}
        step={2}
        numSteps={7}
      >
        <h2>Introduction</h2>
        <Form>
          <FormFieldset>
            <FormFieldsetHeader>
              <FormLegend>Introduction</FormLegend>
            </FormFieldsetHeader>
            <FormFieldsetBody>
              <FormGroup>
                <FormGroupHeader>
                  <FormLabel>Introduce the algorithm</FormLabel>
                  <FormToolbar>
                    <InfoButton text={t.introduction} />
                  </FormToolbar>
                </FormGroupHeader>
                <FormGroupBody>
                  <FreeEditor
                    initialValue={introduction}
                    save={(document) => {
                      update(atbd_id, atbd_version, {
                        introduction: document
                      });
                    }}
                  />
                </FormGroupBody>
              </FormGroup>
            </FormFieldsetBody>
          </FormFieldset>
        </Form>

        <FormFieldset>
          <FormFieldsetHeader>
            <FormLegend>Historical Perspective</FormLegend>
          </FormFieldsetHeader>
          <FormFieldsetBody>
            <FormGroup>
              <FormGroupHeader>
                <FormLabel>Describe the historical perspective</FormLabel>
                <FormToolbar>
                  <InfoButton text={t.historical_perspective} />
                </FormToolbar>
              </FormGroupHeader>
              <FormGroupBody>
                <FreeEditor
                  initialValue={historical_perspective}
                  save={(document) => {
                    update(atbd_id, atbd_version, {
                      historical_perspective: document
                    });
                  }}
                />
              </FormGroupBody>
            </FormGroup>
          </FormFieldsetBody>
        </FormFieldset>
      </EditPage>
    </Inpage>
  );
}

Introduction.propTypes = {
  atbdVersion: PropTypes.object,
  update: PropTypes.func,
  t: PropTypes.object
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion,
  t: state.application.t ? state.application.t.introduction : {}
});

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(Introduction);
