import styled from 'styled-components';
import Constrainer from '../../styles/atoms/Constrainer';
import { themeVal } from '../../styles/utils/general';

export const Inner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  padding: ${themeVal('layout.space')};
`;

export const PageTitle = styled.h2`
  font-size: 1.5rem;
  line-height: 1.8;
  margin: 0;
`;
