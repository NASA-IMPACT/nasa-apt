import styled from 'styled-components';
import Constrainer from '../../styles/atoms/Constrainer';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';

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

const PageSection = styled.div`
  padding: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

export default PageSection;
