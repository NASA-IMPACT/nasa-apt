import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import {
  updateAtbd
} from '../actions/actions';

import CitationForm from './CitationForm';
import EditPage from './common/EditPage';
import { Inpage } from './common/Inpage';
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
import Button from '../styles/button/button';
import AddBtn from '../styles/button/add';

export class IdentifyingInformation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      title: '',
      titleEmpty: false,

      // Hide the citation form by default,
      // as it's not required and also very long.
      showCitationForm: false
    };
    this.onTextFieldChange = this.onTextFieldChange.bind(this);
    this.onTextFieldBlur = this.onTextFieldBlur.bind(this);
    this.updateAtbdTitle = this.updateAtbdTitle.bind(this);
    this.toggleCitationForm = this.toggleCitationForm.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const { atbd } = nextProps;
    const { atbd: prevAtbd } = this.props;
    // New ATBD fetch
    if (atbd && atbd !== prevAtbd) {
      this.setState({
        title: atbd.title
      });
    }
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

  updateAtbdTitle(e) {
    e.preventDefault();
    const {
      updateAtbd: update,
      atbd
    } = this.props;
    const { atbd_id } = atbd;
    const { title } = this.state;
    update(atbd_id, { title });
  }

  toggleCitationForm() {
    this.setState(state => ({
      showCitationForm: !state.showCitationForm
    }));
  }

  render() {
    const {
      atbd,
      hasCitation,
      t
    } = this.props;

    let returnValue;

    if (atbd) {
      const {
        title: atbdTitle,
        titleEmpty,
        showCitationForm
      } = this.state;
      const {
        onTextFieldChange,
        onTextFieldBlur,
        updateAtbdTitle
      } = this;

      const {
        title,
        atbd_id
      } = atbd;

      returnValue = (
        <Inpage>
          <EditPage
            title={title || ''}
            id={atbd_id}
            step={1}
          >
            <h2>Identifying Information</h2>

            <Form>
              <FormFieldset>
                <FormFieldsetHeader>
                  <FormLegend>General</FormLegend>
                </FormFieldsetHeader>
                <FormFieldsetBody>
                  <FormGroup>
                    <FormGroupHeader>
                      <FormLabel htmlFor="atbd-title">Title</FormLabel>
                      <FormToolbar>
                        <InfoButton text={t.title} />
                      </FormToolbar>
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
                  <Button
                    onClick={updateAtbdTitle}
                    variation="base-raised-light"
                    size="large"
                    type="submit"
                  >
                    Save
                  </Button>
                </FormFieldsetBody>
              </FormFieldset>
            </Form>

            <FormFieldset>
              <FormFieldsetHeader>
                <FormLegend>Citation</FormLegend>
              </FormFieldsetHeader>
              <FormFieldsetBody>
                <FormGroup>
                  {showCitationForm ? <CitationForm /> : (
                    <FormGroupBody>
                      {hasCitation ? (
                        <Button
                          variation="base-raised-light"
                          size="large"
                          onClick={this.toggleCitationForm}
                        >
                          Update citation
                        </Button>
                      ) : (
                        <AddBtn
                          variation="base-raised-light"
                          size="large"
                          onClick={this.toggleCitationForm}
                        >
                          Add a citation
                        </AddBtn>
                      )}
                    </FormGroupBody>
                  )}
                </FormGroup>
              </FormFieldsetBody>
            </FormFieldset>
          </EditPage>
        </Inpage>
      );
    } else {
      returnValue = <div>Loading</div>;
    }
    return returnValue;
  }
}

IdentifyingInformation.propTypes = {
  updateAtbd: PropTypes.func,
  atbd: PropTypes.object,
  t: PropTypes.object,
  hasCitation: PropTypes.bool
};

const mapStateToProps = (state) => {
  const { application: app } = state;
  const { atbdVersion, atbdCitation, t } = app;
  const atbd = atbdVersion ? atbdVersion.atbd : null;
  return {
    atbd,
    hasCitation: Boolean(atbdCitation),
    t: t ? t.identifying_information : {}
  };
};

const mapDispatch = {
  updateAtbd
};

export default connect(mapStateToProps, mapDispatch)(IdentifyingInformation);
