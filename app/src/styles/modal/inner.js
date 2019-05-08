import styled from 'styled-components';
import { themeVal } from '../utils/general';
import collecticon from '../collecticons';
import Button from '../button/button';

export const ModalInner = styled.div`
  background: ${themeVal('color.mist')};
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${themeVal('layout.space')};
  padding: 2rem;
  position: relative;
`;

export const CloseModal = styled(Button)`
  position: absolute;
  right: 0;
  top: 0;
  ::before {
    ${collecticon('xmark--small')}
  }
`;
