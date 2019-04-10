import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import collecticon from '../styles/collecticons';
import { themeVal } from '../styles/utils/general';
import { multiply } from '../styles/utils/math';

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
  &::before {
    font-size: 0.875rem;
    margin-right: ${multiply(themeVal('layout.space'), 0.5)};
    ${props => collecticon(props.icon.icon)}
  }
`;

const EditorFigureTool = (props) => {
  const {
    upload,
    active,
    icon
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
              upload({ file: event.currentTarget.files[0] });
            }
          }
        }
      />
      <FigureInputLabel
        active={active}
        htmlFor="file"
        icon={icon}
      >
        Figure
      </FigureInputLabel>
    </Fragment>
  );
};

EditorFigureTool.propTypes = {
  upload: PropTypes.func.isRequired,
  active: PropTypes.bool,
  icon: PropTypes.object.isRequired
};

export default EditorFigureTool;
