import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import isUrl from 'is-url';
import uuid from 'uuid';

import FreeEditor from './FreeEditor';
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
import FormLegend from '../styles/form/legend';
import FormLabel from '../styles/form/label';
import FormInput from '../styles/form/input';
import {
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import RemoveButton from '../styles/button/remove';
import AddBtn from '../styles/button/add';
import { isBlankDocument } from './editorBlankDocument';

class ImplementationInnerForm extends Component {
  constructor(props) {
    super(props);
    const { initialValue } = props;
    const { url = '' } = initialValue;
    this.state = {
      url,
      urlInvalid: false,
      descriptionInvalid: false
    };
    this.onUrlChange = this.onUrlChange.bind(this);
    this.onUrlBlur = this.onUrlBlur.bind(this);
    this.onSave = this.onSave.bind(this);
  }

  onUrlChange(e) {
    this.setState({ url: e.currentTarget.value });
  }

  onUrlBlur() {
    const { url } = this.state;
    if (url.length && !isUrl(url)) {
      this.setState({ urlInvalid: true });
    } else {
      this.setState({ urlInvalid: false });
    }
  }

  onSave(description) {
    const { url } = this.state;
    const urlInvalid = !isUrl(url);
    const descriptionInvalid = isBlankDocument(description);
    this.setState({
      urlInvalid,
      descriptionInvalid
    });

    if (!urlInvalid && !descriptionInvalid) {
      const { save } = this.props;
      save({
        url,
        description
      });
    }
  }

  render() {
    const {
      id,
      label,
      initialValue,
      del,
      t
    } = this.props;

    const {
      url,
      urlInvalid,
      descriptionInvalid
    } = this.state;

    const {
      onUrlChange,
      onUrlBlur,
      onSave
    } = this;

    return (
      <Form>
        <FormFieldset>
          <FormFieldsetHeader>
            <FormLegend>{label}</FormLegend>
            {!!del && (
              <RemoveButton
                variation="base-plain"
                size="small"
                hideText
                onClick={del}
              >
                Remove fieldset
              </RemoveButton>
            )}
          </FormFieldsetHeader>

          <FormFieldsetBody>
            <FormGroup>
              <FormGroupHeader>
                <FormLabel htmlFor={`${id}-url`}>URL</FormLabel>
                <FormToolbar>
                  <InfoButton text={t.url} />
                </FormToolbar>
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id={`${id}-url`}
                  placeholder="Enter a URL"
                  value={url}
                  onChange={onUrlChange}
                  onBlur={onUrlBlur}
                  invalid={urlInvalid}
                />
                {urlInvalid && (
                  <FormHelper>
                    <FormHelperMessage>Please enter a valid URL.</FormHelperMessage>
                  </FormHelper>
                )}
              </FormGroupBody>
            </FormGroup>
            <FormGroup>
              <FormGroupHeader>
                <FormLabel>Description</FormLabel>
                <FormToolbar>
                  <InfoButton text={t.description} />
                </FormToolbar>
              </FormGroupHeader>
              <FormGroupBody>
                <FreeEditor
                  initialValue={initialValue.description}
                  save={onSave}
                  invalid={descriptionInvalid}
                />
                {descriptionInvalid && (
                  <FormHelper>
                    <FormHelperMessage>This field is required.</FormHelperMessage>
                  </FormHelper>
                )}
              </FormGroupBody>
            </FormGroup>
          </FormFieldsetBody>

        </FormFieldset>
      </Form>
    );
  }
}

ImplementationInnerForm.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  initialValue: PropTypes.object,
  save: PropTypes.func,
  del: PropTypes.func,
  t: PropTypes.object
};

class ImplementationForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      newFields: []
    };
    this.addField = this.addField.bind(this);
    this.removeField = this.removeField.bind(this);
  }

  addField() {
    const { newFields } = this.state;
    const next = newFields.concat([uuid()]);
    this.setState({ newFields: next });
  }

  removeField(id) {
    const { newFields } = this.state;
    const next = newFields.filter(d => d !== id);
    this.setState({ newFields: next });
  }

  render() {
    const {
      title,
      data,
      id,
      idProperty,
      urlProperty,
      descriptionProperty,
      t,
      create,
      update,
      del,
      atbdVersion
    } = this.props;

    const {
      atbd,
      atbd_version
    } = atbdVersion;
    const { atbd_id } = atbd;

    const {
      addField,
      removeField
    } = this;

    const { newFields } = this.state;
    const existingFields = data.map(d => ({
      id: d[idProperty],
      url: d[urlProperty],
      description: d[descriptionProperty]
    }));

    return (
      <FormFieldset>
        <FormFieldsetHeader>
          <FormLegend>{title}</FormLegend>
        </FormFieldsetHeader>
        <FormFieldsetBody>

          <FormGroupHeader>
            <FormLabel>Current fields</FormLabel>
          </FormGroupHeader>
          <FormGroupBody>
            {existingFields.map((d, i) => (
              <ImplementationInnerForm
                id={`${id}-existing-${d.id}`}
                key={`${id}-existing-${d.id}`}
                label={`${title} #${i + 1}`}
                initialValue={d}
                t={t}
                del={() => del(d.id)}
                save={({ url, description }) => {
                  update(d.id, {
                    [urlProperty]: url,
                    [descriptionProperty]: description
                  });
                }}
              />
            ))}
            {!data.length && (
              <FormFieldset>
                <FormFieldsetBody>
                  <FormHelper>
                    <FormHelperMessage>No current fields. Add one below.</FormHelperMessage>
                  </FormHelper>
                </FormFieldsetBody>
              </FormFieldset>
            )}
          </FormGroupBody>

          <FormGroupHeader>
            <FormLabel>New fields</FormLabel>
          </FormGroupHeader>
          <FormGroupBody>
            {newFields.map((newId, i) => (
              <ImplementationInnerForm
                id={`${newId}`}
                key={`${newId}`}
                label={`New ${title} #${i + 1}`}
                initialValue={{}}
                t={t}
                del={() => removeField(newId)}
                save={({ url, description }) => {
                  create({
                    atbd_id,
                    atbd_version,
                    [urlProperty]: url,
                    [descriptionProperty]: description
                  });
                  removeField(newId);
                }}
              />
            ))}
          </FormGroupBody>

          <AddBtn variation="base-plain" onClick={addField}>
            Add
          </AddBtn>

        </FormFieldsetBody>
      </FormFieldset>
    );
  }
}

ImplementationForm.propTypes = {
  title: PropTypes.string,
  data: PropTypes.array,
  id: PropTypes.string.isRequired,
  idProperty: PropTypes.string.isRequired,
  urlProperty: PropTypes.string.isRequired,
  descriptionProperty: PropTypes.string.isRequired,
  t: PropTypes.object,
  create: PropTypes.func,
  update: PropTypes.func,
  del: PropTypes.func,
  atbdVersion: PropTypes.object
};

const mapStateToProps = state => ({
  atbdVersion: state.application.atbdVersion
});

export default connect(mapStateToProps)(ImplementationForm);
