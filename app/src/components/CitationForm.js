import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import Form from '../styles/form/form';
import {
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import FormLabel from '../styles/form/label';
import FormInput from '../styles/form/input';
import Button from '../styles/button/button';
import InfoButton from './common/InfoButton';
import FormToolbar from '../styles/form/toolbar';

import {
  createCitation,
  updateCitation
} from '../actions/actions';

export class CitationForm extends Component {
  constructor(props) {
    super(props);
    const { citation } = props;
    const state = {
      creators: '',
      editors: '',
      title: '',
      series_name: '',
      release_date: '',
      release_place: '',
      publisher: '',
      version: '',
      issue: '',
      additional_details: '',
      online_resource: ''
    };
    if (citation) {
      Object.keys(state).forEach((key) => {
        // Avoid adding properties like atbd_id, atbd_version to state.
        if (Object.prototype.hasOwnProperty.call(state, key) && citation[key]) {
          state[key] = citation[key];
        }
      });
    }
    this.state = state;
    this.onTextFieldChange = this.onTextFieldChange.bind(this);
    this.saveCitation = this.saveCitation.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const { citation } = nextProps;
    const { citation: prevCitation } = this.props;
    if (citation && citation !== prevCitation) {
      this.setState(citation);
    }
  }

  onTextFieldChange(e, prop) {
    this.setState({
      [prop]: e.currentTarget.value
    });
  }

  saveCitation(e) {
    e.preventDefault();
    const {
      citation,
      atbd_id,
      atbd_version,
      createCitation: create,
      updateCitation: update
    } = this.props;

    // Determine whether to create or update existing.
    const hasExisting = !!citation
      && citation.atbd_version === atbd_version
      && citation.atbd_id === atbd_id;

    const method = hasExisting ? update.bind(null, citation.citation_id)
      : create;

    const document = { ...this.state };
    Object.keys(document).forEach((key) => {
      if (!document[key]) {
        delete document[key];
      }
    });

    if (!hasExisting) {
      Object.assign(document, { atbd_id, atbd_version });
    }

    method(document);
  }

  render() {
    const {
      creators,
      editors,
      title,
      series_name,
      release_date,
      release_place,
      publisher,
      version,
      issue,
      additional_details,
      online_resource
    } = this.state;

    const { t } = this.props;

    const {
      onTextFieldChange,
      saveCitation
    } = this;

    return (
      <Form>
        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-creators">Creators</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_creators} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-creators"
            placeholder="Enter one or multiple citation creator(s)"
            value={creators}
            onChange={e => onTextFieldChange(e, 'creators')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-editors">Editors</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_editors} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-editors"
            placeholder="Enter one or multiple citation editor(s)"
            value={editors}
            onChange={e => onTextFieldChange(e, 'editors')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-title">Title</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_title} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-title"
            placeholder="Enter the citation title"
            value={title}
            onChange={e => onTextFieldChange(e, 'title')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-series">Series Name</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_series} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-series"
            placeholder="Enter the citation series name"
            value={series_name}
            onChange={e => onTextFieldChange(e, 'series_name')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-release-date">Release Date</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_release_date} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-release-date"
            placeholder="Enter the citation release date"
            value={release_date}
            onChange={e => onTextFieldChange(e, 'release_date')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-release-place">Release Place</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_release_place} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-release-place"
            placeholder="Enter the citation release place"
            value={release_place}
            onChange={e => onTextFieldChange(e, 'release_place')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-publisher">Publisher</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_publisher} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-publisher"
            placeholder="Enter the citation publisher"
            value={publisher}
            onChange={e => onTextFieldChange(e, 'publisher')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-version">Version</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_version} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-version"
            placeholder="Enter the citation version"
            value={version}
            onChange={e => onTextFieldChange(e, 'version')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-issue">Issue</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_issue} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-issue"
            placeholder="Enter the citation issue"
            value={issue}
            onChange={e => onTextFieldChange(e, 'issue')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-details">Additional Details</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_additional_details} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-details"
            placeholder="Enter any additional citation details"
            value={additional_details}
            onChange={e => onTextFieldChange(e, 'additional_details')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-url">Online Resource</FormLabel>
          <FormToolbar>
            <InfoButton text={t.citation_online_resource} />
          </FormToolbar>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-url"
            placeholder="Enter the citation URL"
            value={online_resource}
            onChange={e => onTextFieldChange(e, 'online_resource')}
          />
          <Button
            onClick={saveCitation}
            variation="base-raised-light"
            size="large"
            type="submit"
          >
            Save
          </Button>
        </FormGroupBody>
      </Form>
    );
  }
}

CitationForm.propTypes = {
  citation: PropTypes.object,
  t: PropTypes.object,
  createCitation: PropTypes.func,
  updateCitation: PropTypes.func,
  atbd_id: PropTypes.number,
  atbd_version: PropTypes.number
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const { atbdVersion, t, atbdCitation: citation } = app;
  const atbd_version = atbdVersion ? atbdVersion.atbd_version : null;
  const atbd_id = atbdVersion ? atbdVersion.atbd_id : null;
  return {
    atbd_id,
    atbd_version,
    citation,
    t: t ? t.identifying_information : {}
  };
};

const mapDispatch = {
  createCitation,
  updateCitation
};

export default connect(mapStateToProps, mapDispatch)(CitationForm);
