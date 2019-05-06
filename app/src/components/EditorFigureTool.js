import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import collecticon from '../styles/collecticons';
import Button from '../styles/button/button';

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

const FigureLabel = styled.label`
  display: block;
  width: 100%;
  height: 100%
`;

const EditorFigureTool = (props) => {
  const {
    upload,
    active,
  } = props;

  return (
    <Fragment>
      <FigureInput
        id="file"
        type="file"
        accept=".png,.jpg,.jpeg"
        onChange={
          (event) => {
            if (event.currentTarget.files.length) {
              upload(event.currentTarget.files[0]);
            }
          }
        }
      />
      <FigureButton
        active={active}
      >
        <FigureLabel
          htmlFor="file"
        >
          Figure
        </FigureLabel>
      </FigureButton>
    </Fragment>
  );
};

EditorFigureTool.propTypes = {
  upload: PropTypes.func.isRequired,
  active: PropTypes.bool
};

export default EditorFigureTool;
