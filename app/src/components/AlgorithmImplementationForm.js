import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Value } from 'slate';
import isUrl from 'is-url';
import Plain from 'slate-plain-serializer';

import FreeEditor from './FreeEditor';
import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import {
  FormFieldset
} from '../styles/form/fieldset';
import FormLegend from '../styles/form/legend';
import FormLabel from '../styles/form/label';
import FormInput from '../styles/form/input';
import {
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import { getValidOrBlankDocument } from './editorBlankDocument';

class AlgorithmImplementationForm extends Component {
  constructor(props) {
    super(props);
    const { accessUrl = '' } = props;
    this.state = {
      accessUrl,
      accessUrlInvalid: false,
      executionDescriptionInvalid: false
    };
    this.onAccessUrlChange = this.onAccessUrlChange.bind(this);
    this.onAccessUrlBlur = this.onAccessUrlBlur.bind(this);
    this.onSave = this.onSave.bind(this);
  }

  onAccessUrlChange(e) {
    this.setState({ accessUrl: e.currentTarget.value });
  }

  onAccessUrlBlur() {
    const { accessUrl } = this.state;
    if (accessUrl.length && !isUrl(accessUrl)) {
      this.setState({ accessUrlInvalid: true });
    } else {
      this.setState({ accessUrlInvalid: false });
    }
  }

  onSave(executionDescription) {
    const { accessUrl } = this.state;
    const accessUrlInvalid = !isUrl(accessUrl);
    const executionDescriptionInvalid = !Plain.serialize(executionDescription).length;
    this.setState({
      accessUrlInvalid,
      executionDescriptionInvalid
    });
  }

  render() {
    const {
      id,
      label,
      executionDescription,
      save
    } = this.props;
    const {
      accessUrl,
      accessUrlInvalid,
      executionDescriptionInvalid
    } = this.state;
    const {
      onAccessUrlChange,
      onAccessUrlBlur,
      onSave
    } = this;
    return (
      <FormFieldset>
        <FormGroup>
          {!!label && <FormLegend>{label}</FormLegend>}
          <FormGroupHeader>
            <FormLabel htmlFor={`${id}-access`}>Access URL</FormLabel>
            {accessUrlInvalid && (
              <FormHelper>
                <FormHelperMessage>Please enter a valid URL.</FormHelperMessage>
              </FormHelper>
            )}
          </FormGroupHeader>
          <FormGroupBody>
            <FormInput
              type="text"
              size="large"
              id={`${id}-access`}
              placeholder="Enter an access URL"
              value={accessUrl}
              onChange={onAccessUrlChange}
              onBlur={onAccessUrlBlur}
              invalid={accessUrlInvalid}
            />
          </FormGroupBody>
        </FormGroup>
        <FormGroup>
          <FormGroupHeader>
            <FormLabel>Execution Description</FormLabel>
            {executionDescriptionInvalid && (
              <FormHelper>
                <FormHelperMessage>This field is required.</FormHelperMessage>
              </FormHelper>
            )}
          </FormGroupHeader>
          <FreeEditor
            value={Value.fromJSON(getValidOrBlankDocument(executionDescription))}
            save={onSave}
            invalid={executionDescriptionInvalid}
            externalSaveBtn
          />
        </FormGroup>
      </FormFieldset>
    );
  }
}

AlgorithmImplementationForm.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  accessUrl: PropTypes.string,
  executionDescription: PropTypes.object,
  save: PropTypes.func
};

export default AlgorithmImplementationForm;
