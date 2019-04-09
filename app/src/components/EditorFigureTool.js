import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import styled from 'styled-components/macro';
import { themeVal } from '../styles/utils/general';
import { uploadFile } from '../actions/actions';

const FigureInput = styled.input`
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
`;

const FigureInputLabel = styled.label`
  cursor: pointer;
  background: ${props => (props.active ? themeVal('color.shadow') : null)};
  box-shadow: ${props => (props.active ? themeVal('boxShadow.inset') : null)};
  font-weight: bold;
  line-height: 1;
  padding: .5rem 1rem;
  transition: background .16s ease;
  &:hover {
    background: ${themeVal('color.shadow')}
  }
`;

const EditorFigureTool = (props) => {
  const { uploadFile: upload } = props;
  return (
    <Fragment>
      <FigureInput
        id="file"
        type="file"
        onChange={
          (event) => { upload({ file: event.currentTarget.files[0] }); }
        }
      />
      <FigureInputLabel
        htmlFor="file"
      >
        Figure
      </FigureInputLabel>
    </Fragment>
  );
};

const mapDispatch = { uploadFile };

export default connect(null, mapDispatch)(EditorFigureTool);
