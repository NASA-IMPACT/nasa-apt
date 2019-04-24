import styled from 'styled-components';
import { themeVal } from '../utils/general';
import { multiply } from '../utils/math';

export const FormFieldset = styled.div`
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${multiply(themeVal('layout.space'), 2)};
  background-color: ${themeVal('color.mist')};
  padding: ${multiply(themeVal('layout.space'), 2)};
  border-radius: ${themeVal('shape.rounded')};
`;

export const FormFieldsetHeader = styled.div`
  display: flex;
  flex-flow: wrap nowrap;
  justify-content: space-between;
`;
