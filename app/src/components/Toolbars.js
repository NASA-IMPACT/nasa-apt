import styled from 'styled-components';
import collecticon from '../styles/collecticons';
import { multiply } from '../styles/utils/math';
import { themeVal } from '../styles/utils/general';

export const ToolbarAction = styled('span')`
  cursor: pointer;
  font-weight: bold;
`;

export const ToolbarIcon = styled.span`
  line-height: 1;
  &::before {
    ${collecticon('text-block')}
  }
`;

export const Toolbar = styled.div`
  align-items: center;
  background-color: ${themeVal('color.shadow')};
  border: 1px solid #CCC;
  border-top-left-radius: ${multiply(themeVal('layout.space'), 0.25)};
  border-top-right-radius: ${multiply(themeVal('layout.space'), 0.25)};
  display: flex;
  padding: ${multiply(themeVal('layout.space'), 0.75)} ${themeVal('layout.space')};
  position: relative;
`;

export const ToolbarLabel = styled.span`
  color: ${themeVal('color.darkgray')};
  font-size: 0.875rem;
  font-weight: lighter;
  text-transform: uppercase;
`;
