import styled from 'styled-components';
import collecticon from '../styles/collecticons';
import { multiply } from '../styles/utils/math';
import { themeVal } from '../styles/utils/general';

export const ToolbarAction = styled('span')`
  cursor: pointer;
  background: ${props => (props.active ? themeVal('color.shadow') : null)};
  box-shadow: ${props => (props.active ? themeVal('boxShadow.inset') : null)};
  font-weight: bold;
  line-height: 1;
  padding: .5rem 1rem;
  transition: background .16s ease;
  visibility: ${props => (props.hidden ? 'hidden' : 'visible')};
  &:hover {
    background: ${themeVal('color.shadow')}
  }
`;

export const ToolbarIcon = styled.span`
  display: flex;
  &::before {
    font-size: 0.875rem;
    margin-right: ${multiply(themeVal('layout.space'), 0.5)};
    ${props => collecticon(props.icon.icon)}
  }
`;

export const Toolbar = styled.div`
  align-items: center;
  background: ${themeVal('color.shadow')};
  border: 1px solid ${themeVal('color.gray')};
  border-top-left-radius: ${multiply(themeVal('layout.space'), 0.25)};
  border-top-right-radius: ${multiply(themeVal('layout.space'), 0.25)};
  display: flex;
  padding: 0 3rem;
  position: relative;
`;

export const ToolbarLabel = styled.span`
  color: ${themeVal('color.darkgray')};
  font-size: 0.875rem;
  font-weight: lighter;
  margin-right: ${themeVal('layout.space')};
  text-transform: uppercase;
`;
