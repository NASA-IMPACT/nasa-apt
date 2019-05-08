import React, { Component, Fragment } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';

import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';
import { uploadFile } from '../actions/actions';
import {
  showGlobalLoading,
  hideGlobalLoading
} from './common/OverlayLoader';

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
import { ModalInner, CloseModal } from '../styles/modal/inner';

const FigureInput = styled.input`
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
`;

const FigureButton = styled(Button)`
  ::before {
    ${collecticon('picture')}
  }
`;

// These styles ensure you can click anywhere in the parent button
// and still trigger the file upload UI.
const UploadButton = styled(Button)`
  padding: 0;
  label,
  > span {
    display: block;
    width: 100%;
  }
  label {
    padding: 0.5rem 1.25rem;
  }
`;

const Figure = styled.figure`
  display: flex;
  justify-content: center;
  > img {
    width: 320px;
    height: 100%;
  }
`;

export class EditorFigureTool extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeModal: false,
      hasUploadedImage: false,
      caption: ''
    };
    this.setModalState = this.setModalState.bind(this);
    this.onCaptionChange = this.onCaptionChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);
    this.onFileSelect = this.onFileSelect.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const { uploadedFile } = nextProps;
    const { uploadedFile: lastUploadState } = this.props;
    if (uploadedFile !== lastUploadState) {
      this.setState({
        hasUploadedImage: true
      });
      hideGlobalLoading();
    }
  }

  setModalState(nextState) {
    this.setState({
      activeModal: !!nextState,
      hasUploadedImage: false,
      caption: ''
    });
  }

  onCaptionChange(e) {
    this.setState({
      caption: e.currentTarget.value
    });
  }

  onSubmit(e) {
    e.preventDefault();
    const {
      hasUploadedImage,
      caption
    } = this.state;
    const {
      onSaveSuccess,
      uploadedFile
    } = this.props;

    if (hasUploadedImage) {
      onSaveSuccess(uploadedFile, caption);
      this.resetForm();
    }
  }

  onFileSelect(e) {
    const { uploadFile: upload } = this.props;
    if (e.currentTarget.files.length) {
      upload(e.currentTarget.files[0]);
      showGlobalLoading();
    }
  }

  resetForm() {
    this.setState({
      activeModal: false,
      hasUploadedImage: false,
      caption: ''
    });
  }

  render() {
    const {
      active,
      uploadedFile
    } = this.props;

    const {
      activeModal,
      hasUploadedImage,
      caption
    } = this.state;

    const {
      setModalState,
      onCaptionChange,
      onSubmit,
      onFileSelect
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
                <FormLabel>Upload an image</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <FigureInput
                  id="file-upload"
                  type="file"
                  accept=".png,.jpg,.jpeg"
                  onChange={onFileSelect}
                />
                <UploadButton
                  variation="base-raised-light"
                  size="large"
                >
                  <FormLabel htmlFor="file-upload">Choose an image to upload</FormLabel>
                </UploadButton>
                {!hasUploadedImage && (
                  <FormHelper>
                    <FormHelperMessage>Please choose an image to upload.</FormHelperMessage>
                  </FormHelper>
                )}
                {!!hasUploadedImage && (
                  <Figure>
                    <img
                      src={uploadedFile}
                      alt="Successfully uploaded"
                    />
                  </Figure>
                )}
              </FormGroupBody>

              <FormGroupHeader>
                <FormLabel htmlFor="image-caption">Image caption</FormLabel>
              </FormGroupHeader>
              <FormGroupBody>
                <FormInput
                  type="text"
                  size="large"
                  id="image-caption"
                  placeholder="Enter a caption"
                  value={caption}
                  onChange={onCaptionChange}
                />
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

        <FigureButton
          onClick={() => setModalState(true)}
          variation="base-plain"
          size="large"
          active={active}
        >
          Figure
        </FigureButton>
      </Fragment>
    );
  }
}

EditorFigureTool.propTypes = {
  uploadFile: PropTypes.func.isRequired,
  onSaveSuccess: PropTypes.func.isRequired,
  active: PropTypes.bool,
  uploadedFile: PropTypes.string
};

const mapStateToProps = state => ({
  uploadedFile: state.application.uploadedFile
});

const mapDispatch = {
  uploadFile
};

export default connect(mapStateToProps, mapDispatch)(EditorFigureTool);
