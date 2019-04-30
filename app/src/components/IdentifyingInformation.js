import React, { Component } from 'react';
import { connect } from 'react-redux';

import EditPage from './common/EditPage';
import { Inpage } from './common/Inpage';
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
import AddBtn from '../styles/button/add';

export class IdentifyingInformation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: '',
      titleEmpty: false,

      doiName: '',
      doiNameEmpty: false,
      doiAuthority: '',

      // Hide the citation form by default,
      // as it's not required and also very long.
      showCitationForm: false,

      citationCreators: '',
      citationEditors: '',
      citationTitle: '',
      citationSeries: '',
      citationReleaseDate: '',
      citationReleasePlace: '',
      citationPublisher: '',
      citationVersion: '',
      citationIssue: '',
      citationDetails: '',
      citationUrl: ''
    };
    this.onTextFieldChange = this.onTextFieldChange.bind(this);
    this.onTextFieldBlur = this.onTextFieldBlur.bind(this);
    this.toggleCitationForm = this.toggleCitationForm.bind(this);
  }

  onTextFieldChange(e, prop) {
    this.setState({
      [prop]: e.currentTarget.value
    });
  }

  onTextFieldBlur(e, prop) {
    const empty = !e.currentTarget.value;
    this.setState({
      [prop]: empty
    });
  }

  toggleCitationForm() {
    this.setState(state => ({
      showCitationForm: !state.showCitationForm
    }));
  }

  renderCitation() {
    const {
      citationCreators,
      citationEditors,
      citationTitle,
      citationSeries,
      citationReleaseDate,
      citationReleasePlace,
      citationPublisher,
      citationVersion,
      citationIssue,
      citationDetails,
      citationUrl
    } = this.state;

    const {
      onTextFieldChange
    } = this;

    return (
      <React.Fragment>
        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-creators">Creators</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-creators"
            placeholder="Enter one or multiple citation creator(s)"
            value={citationCreators}
            onChange={e => onTextFieldChange(e, 'citationCreators')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-editors">Editors</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-editors"
            placeholder="Enter one or multiple citation editor(s)"
            value={citationEditors}
            onChange={e => onTextFieldChange(e, 'citationEditors')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-title">Title</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-title"
            placeholder="Enter the citation title"
            value={citationTitle}
            onChange={e => onTextFieldChange(e, 'citationTitle')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-series">Series Name</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-series"
            placeholder="Enter the citation series name"
            value={citationSeries}
            onChange={e => onTextFieldChange(e, 'citationSeries')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-release-date">Release Date</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-release-date"
            placeholder="Enter the citation release date"
            value={citationReleaseDate}
            onChange={e => onTextFieldChange(e, 'citationReleaseDate')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-release-place">Release Place</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-release-place"
            placeholder="Enter the citation release place"
            value={citationReleasePlace}
            onChange={e => onTextFieldChange(e, 'citationReleasePlace')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-publisher">Publisher</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-publisher"
            placeholder="Enter the citation publisher"
            value={citationPublisher}
            onChange={e => onTextFieldChange(e, 'citationPublisher')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-version">Version</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-version"
            placeholder="Enter the citation version"
            value={citationVersion}
            onChange={e => onTextFieldChange(e, 'citationVersion')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-issue">Issue</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-issue"
            placeholder="Enter the citation issue"
            value={citationIssue}
            onChange={e => onTextFieldChange(e, 'citationIssue')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-details">Additional Details</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-details"
            placeholder="Enter any additional citation details"
            value={citationDetails}
            onChange={e => onTextFieldChange(e, 'citationDetails')}
          />
        </FormGroupBody>

        <FormGroupHeader>
          <FormLabel htmlFor="atbd-citation-url">Online Resource</FormLabel>
        </FormGroupHeader>
        <FormGroupBody>
          <FormInput
            type="text"
            size="large"
            id="atbd-citation-url"
            placeholder="Enter the citation URL"
            value={citationUrl}
            onChange={e => onTextFieldChange(e, 'citationUrl')}
          />
        </FormGroupBody>
      </React.Fragment>
    );
  }

  render() {
    const {
      title: atbdTitle,
      titleEmpty,
      doiName,
      doiNameEmpty,
      doiAuthority,
      showCitationForm
    } = this.state;
    const {
      onTextFieldChange,
      onTextFieldBlur
    } = this;

    let returnValue;
    let title = 'New ATBD';

    returnValue = (
      <Inpage>
        <EditPage
          title={title || ''}
          id={1}
          step={1}
        >
          <h2>Identifying Information</h2>

          <FormFieldset>
            <FormGroup>
              <FormFieldsetHeader>
                <FormLegend>General</FormLegend>
              </FormFieldsetHeader>
              <FormGroupHeader>
                <FormLabel htmlFor="atbd-title">Title</FormLabel>
                {titleEmpty && (
                  <FormHelper>
                    <FormHelperMessage>Please enter a title.</FormHelperMessage>
                  </FormHelper>
                )}
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id="atbd-title"
                  placeholder="Enter a title"
                  value={atbdTitle}
                  onChange={e => onTextFieldChange(e, 'title')}
                  onBlur={e => onTextFieldBlur(e, 'titleEmpty')}
                  invalid={titleEmpty}
                />
              </FormGroupBody>
            </FormGroup>
          </FormFieldset>

          <FormFieldset>
            <FormGroup>
              <FormFieldsetHeader>
                <FormLegend>DOI</FormLegend>
              </FormFieldsetHeader>
              <FormGroupHeader>
                <FormLabel htmlFor="atbd-doi-name">DOI</FormLabel>
                {doiNameEmpty && (
                  <FormHelper>
                    <FormHelperMessage>Please enter a DOI name.</FormHelperMessage>
                  </FormHelper>
                )}
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id="atbd-doi-name"
                  placeholder="Enter a DOI name"
                  value={doiName}
                  onChange={e => onTextFieldChange(e, 'doiName')}
                  onBlur={e => onTextFieldBlur(e, 'doiNameEmpty')}
                  invalid={doiNameEmpty}
                />
              </FormGroupBody>

              <FormGroupHeader>
                <FormLabel htmlFor="atbd-doi-authority">Authority</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id="atbd-doi-authority"
                  placeholder="Enter a DOI authority"
                  value={doiAuthority}
                  onChange={e => onTextFieldChange(e, 'doiAuthority')}
                />
              </FormGroupBody>
            </FormGroup>
          </FormFieldset>

          <FormFieldset>
            <FormGroup>
              <FormFieldsetHeader>
                <FormLegend>Citation</FormLegend>
              </FormFieldsetHeader>
              {showCitationForm ? this.renderCitation() : (
                <FormGroupBody>
                  <AddBtn
                    variation="base-raised-light"
                    size="large"
                    onClick={this.toggleCitationForm}
                  >
                    Add a citation
                  </AddBtn>
                </FormGroupBody>
              )}
            </FormGroup>
          </FormFieldset>
        </EditPage>
      </Inpage>
    );

    return returnValue;
  }
}

export default connect()(IdentifyingInformation);
