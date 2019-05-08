import React, { Fragment } from 'react';
import { PropTypes as T } from 'prop-types';
import styled from 'styled-components';

import { themeVal } from '../utils/general';

const ModalBg = styled.div`
  background: ${themeVal('color.background')};
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  opacity: 0.98;
  position: fixed;
  z-index: 10;
`;

const ModalContentWrapper = styled.div`
  left: 0;
  margin-top: -10%;
  position: fixed;
  width: 100%;
  z-index: 11;
`;

const ModalContent = styled.div`
  background: ${themeVal('color.background')};
  box-shadow: ${themeVal('boxShadow.input')};
  margin: 0 auto;
  width: 70%;
`;

export default function Modal(props) {
  const {
    children,
    active,
    onBodyClick
  } = props;
  if (!active) return null;
  return (
    <Fragment>
      <ModalBg onClick={onBodyClick} />
      <ModalContentWrapper>
        <ModalContent>
          {children}
        </ModalContent>
      </ModalContentWrapper>
    </Fragment>
  );
}

Modal.propTypes = {
  children: T.node.isRequired,
  active: T.bool,
  onBodyClick: T.func
};
