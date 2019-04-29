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
import FormLabel from '../styles/form/label';
import FormLegend from '../styles/form/legend';

export function Introduction(props) {
  const {
    atbdVersion = {},
    update
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
        <FormFieldset>
          <FormGroup>
            <FormFieldsetHeader>
              <FormLegend>Introduction</FormLegend>
            </FormFieldsetHeader>
            <FormGroupHeader>
              <FormLabel>Introduce the algorithm</FormLabel>
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
        </FormFieldset>

        <FormFieldset>
          <FormGroup>
            <FormFieldsetHeader>
              <FormLegend>Historical Perspective</FormLegend>
            </FormFieldsetHeader>
            <FormGroupHeader>
              <FormLabel>Describe the historical perspective</FormLabel>
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
        </FormFieldset>
      </EditPage>
    </Inpage>
  );
}

Introduction.propTypes = {
  atbdVersion: PropTypes.object,
  update: PropTypes.func
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion
});

const mapDispatchToProps = {
  update: updateAtbdVersion
};

export default connect(mapStateToProps, mapDispatchToProps)(Introduction);
