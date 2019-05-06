import styled from 'styled-components';
import { themeVal } from './utils/general';
import { divide } from './utils/math';

export const HorizontalDivider = styled.hr`
  display: inline-flex;
  border: 0;
  width: ${divide(themeVal('layout.space'), 2)};
  height: 2rem;
  margin: 0 ${themeVal('layout.space')};
  background: transparent linear-gradient(90deg, #FFFFFF, #FFFFFF) 50% / ${themeVal('layout.border')} auto no-repeat;
  opacity: 0.16;
`;

export const VerticalDivider = styled.hr`
  display: inline-flex;
  border: 0;
  width: ${divide(themeVal('layout.space'), 2)};
  height: 2rem;
  margin: 0 ${themeVal('layout.space')};
  background: transparent linear-gradient(90deg, #FFFFFF, #FFFFFF) 50% / ${themeVal('layout.border')} auto no-repeat;
  opacity: 0.16;
`;
