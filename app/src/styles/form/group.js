import styled from 'styled-components';
import { themeVal } from '../utils/general';
import { divide, multiply } from '../utils/math';

export const FormGroup = styled.div`
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${themeVal('layout.space')};
`;

export const FormGroupHeader = styled.div`
  display: flex;
  flex-flow: wrap nowrap;
  justify-content: space-between;
  padding: 0 ${multiply(themeVal('layout.space'), 2)};
`;

export const FormGroupBody = styled.div`
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${divide(themeVal('layout.space'), 2)};
  padding: 0 ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')};
`;
