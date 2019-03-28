import styled from 'styled-components';
import Constrainer from '../../styles/atoms/constrainer';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';

export const Inner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
`;

const PageSection = styled.div`
  margin: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

export default PageSection;
