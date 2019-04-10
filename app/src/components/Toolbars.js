import styled from 'styled-components';
import { multiply } from '../styles/utils/math';
import { themeVal } from '../styles/utils/general';
import Button from '../styles/atoms/button';
import collecticon from '../styles/collecticons';

export const EquationBtn = styled(Button)`
  ::before {
    ${collecticon('equal--small')}
  }
`;

export const ParagraphBtn = styled(Button)`
  ::before {
    ${collecticon('text-block')}
  }
`;

export const TableBtn = styled(Button)`
  ::before {
    ${collecticon('list')}
  }
`;

export const Toolbar = styled.div`
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
