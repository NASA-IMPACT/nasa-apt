import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import isUrl from 'is-url';
import styled from 'styled-components';

import collecticon from '../styles/collecticons';
import FreeEditor from './FreeEditor';
import InfoButton from './common/InfoButton';
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
import FormInput from '../styles/form/input';
import {
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import Button from '../styles/button/button';
import { isBlankDocument } from './editorBlankDocument';

const RemoveButton = styled(Button)`
  ::before {
    ${collecticon('trash-bin')}
  }
`;

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
    const executionDescriptionInvalid = isBlankDocument(executionDescription);
    this.setState({
      accessUrlInvalid,
      executionDescriptionInvalid
    });

    if (!accessUrlInvalid && !executionDescriptionInvalid) {
      const { save } = this.props;
      save({
        accessUrl,
        executionDescription
      });
    }
  }

  render() {
    const {
      id,
      label,
      executionDescription,
      del,
      t
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
          <FormFieldsetHeader>
            <FormLegend>{label}</FormLegend>
            {!!del && (
              <RemoveButton
                variation="base-plain"
                size="small"
                hideText
                onClick={() => del()}
              >
                Remove fieldset
              </RemoveButton>
            )}
          </FormFieldsetHeader>
          <FormGroupHeader>
            <FormLabel htmlFor={`${id}-access`}>
              Access URL
              <InfoButton text={t.access_url} />
            </FormLabel>
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

          <FormGroupHeader>
            <FormLabel>
              Execution Description
              <InfoButton text={t.execution_description} />
            </FormLabel>
            {executionDescriptionInvalid && (
              <FormHelper>
                <FormHelperMessage>This field is required.</FormHelperMessage>
              </FormHelper>
            )}
          </FormGroupHeader>
          <FormGroupBody>
            <FreeEditor
              initialValue={executionDescription}
              save={onSave}
              invalid={executionDescriptionInvalid}
            />
          </FormGroupBody>
        </FormGroup>
      </FormFieldset>
    );
  }
}

AlgorithmImplementationForm.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  accessUrl: PropTypes.string,
  executionDescription: PropTypes.object,
  save: PropTypes.func,
  del: PropTypes.func,
  t: PropTypes.object
};

const mapStateToProps = state => ({
  t: state.application.static ? state.application.static.algorithm_implementation : {}
});

export default connect(mapStateToProps)(AlgorithmImplementationForm);
