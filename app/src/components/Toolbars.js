import styled from 'styled-components';
import { multiply } from '../styles/utils/math';
import { themeVal } from '../styles/utils/general';
import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';

export const EquationBtn = styled(Button)`
  ::before {
    ${collecticon('pi')}
  }
`;

export const ParagraphBtn = styled(Button)`
  ::before {
    ${collecticon('pilcrow')}
  }
`;

export const TableBtn = styled(Button)`
  ::before {
    ${collecticon('table')}
  }
`;

export const Toolbar = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  background: ${themeVal('color.shadow')};
  border-top-left-radius: ${multiply(themeVal('layout.space'), 0.25)};
  border-top-right-radius: ${multiply(themeVal('layout.space'), 0.25)};
  padding: 0 3rem;
`;

export const ToolbarLabel = styled.h5`
  color: ${themeVal('color.darkgray')};
  font-size: 0.875rem;
  font-weight: lighter;
  margin-right: ${themeVal('layout.space')};
  text-transform: uppercase;
`;
