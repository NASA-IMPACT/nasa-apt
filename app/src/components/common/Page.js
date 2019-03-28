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

const PageSection = styled.div`
  margin: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

export default PageSection;
