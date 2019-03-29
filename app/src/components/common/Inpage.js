import styled from 'styled-components';

import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import Constrainer from '../../styles/atoms/Constrainer';

export const Inpage = styled.article`
  display: grid;
  height: 100%;
  grid-template-rows: auto 1fr;
`;

export const InpageHeader = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

export const InpageHeaderInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
  padding: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

export const InpageHeadline = styled.div`

`;

export const InpageTitle = styled.h1`
  font-size: 1.25rem;
  line-height: 1;
  margin: 0;
`;

export const InpageBody = styled.div`

`;

export const InpageBodyInner = styled(Constrainer)`
  padding: ${themeVal('layout.space')};
`;
