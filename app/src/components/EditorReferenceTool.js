import React, { Component, Fragment } from 'react';
import { PropTypes as T } from 'prop-types';
import styled from 'styled-components';

import { themeVal } from '../styles/utils/general';
import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';

import {
  FormGroup,
  FormGroupBody,
  FormGroupHeader
} from '../styles/form/group';
import FormLabel from '../styles/form/label';
import FormInput from '../styles/form/input';
import {
  FormHelper,
  FormHelperMessage
} from '../styles/form/helper';
import Modal from '../styles/modal/modal';

const ModalInner = styled.div`
  background: ${themeVal('color.mist')};
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${themeVal('layout.space')};
  padding: 2rem;
  position: relative;
`;

const CloseModal = styled(Button)`
  position: absolute;
  right: 0;
  top: 0;
  ::before {
    ${collecticon('xmark--small')}
  }
`;

export const ReferenceBtn = styled(Button)`
  ::before {
    ${collecticon('circle-question')}
  }
`;

export class EditorReferenceTool extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeModal: false,
      referenceName: '',
      referenceEmpty: false
    };
    this.setModalState = this.setModalState.bind(this);
    this.onReferenceNameChange = this.onReferenceNameChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
    this.validate = this.validate.bind(this);
  }

  onReferenceNameChange(e) {
    this.setState({
      referenceName: e.currentTarget.value
    });
  }

  onSubmit(e) {
    e.preventDefault();
    const { onSubmit } = this.props;
    const { referenceName } = this.state;
    const nextState = {
      referenceEmpty: !referenceName.length
    };
    if (!nextState.referenceEmpty) {
      onSubmit(referenceName);
      nextState.activeModal = false;
    }
    this.setState(nextState);
  }

  setModalState(nextState) {
    this.setState({
      activeModal: !!nextState
    });
  }

  validate() {
    this.setState(state => ({
      referenceEmpty: !state.referenceName
    }));
  }

  render() {
    const {
      activeModal,
      referenceName,
      referenceEmpty
    } = this.state;

    const {
      setModalState,
      onReferenceNameChange,
      validate,
      onSubmit
    } = this;

    return (
      <Fragment>
        <Modal
          active={activeModal}
          onBodyClick={() => setModalState(false)}
        >
          <ModalInner>
            <FormGroup>
              <FormGroupHeader>
                <FormLabel htmlFor="reference-title">Reference Name</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id="reference-title"
                  placeholder="Enter a title"
                  value={referenceName}
                  onChange={onReferenceNameChange}
                  onBlur={validate}
                />
                {referenceEmpty && (
                  <FormHelper>
                    <FormHelperMessage>Please enter a reference.</FormHelperMessage>
                  </FormHelper>
                )}
              </FormGroupBody>
            </FormGroup>
            <Button
              onClick={onSubmit}
              variation="base-raised-light"
              size="large"
              type="submit"
            >
              Place
            </Button>
            <CloseModal
              onClick={() => setModalState(false)}
              variation="base-plain"
              size="large"
              hideText
            >
              Close
            </CloseModal>
          </ModalInner>
        </Modal>

        <ReferenceBtn
          onClick={() => setModalState(true)}
          variation="base-plain"
          size="large"
        >
          Reference
        </ReferenceBtn>
      </Fragment>
    );
  }
}

EditorReferenceTool.propTypes = {
  onSubmit: T.func
};

export default EditorReferenceTool;
