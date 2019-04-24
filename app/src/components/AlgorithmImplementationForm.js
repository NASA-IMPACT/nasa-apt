import React from 'react';
import PropTypes from 'prop-types';
import { Value } from 'slate';

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
import { getValidOrBlankDocument } from './editorBlankDocument';

function AlgorithmImplementationForm(props) {
  const {
    id,
    label,
    accessUrl = '',
    executionDescription,
    save
  } = props;
  return (
    <FormFieldset>
      <FormGroup>
        {!!label && <FormLegend>{label}</FormLegend>}
        <FormGroupHeader>
          <FormLabel htmlFor={`${id}-access`}>Access URL</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id={`${id}-access`}
            placeholder="Enter an access URL"
            value={accessUrl}
          />
        </FormGroupBody>
      </FormGroup>
      <FormGroup>
        <FormGroupHeader>
          <FormLabel>Execution Description</FormLabel>
        </FormGroupHeader>
        <FreeEditor
          value={Value.fromJSON(getValidOrBlankDocument(executionDescription))}
        />
      </FormGroup>
    </FormFieldset>
  );
}

AlgorithmImplementationForm.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  accessUrl: PropTypes.string,
  executionDescription: PropTypes.object,
  save: PropTypes.func
};

export default AlgorithmImplementationForm;
