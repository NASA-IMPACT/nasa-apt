import styled from 'styled-components/macro';
import { themeVal } from '../utils/general';
import { multiply } from '../utils/math';

const Prose = styled.div`
  font-size: ${themeVal('type.base.size')};                                             // 16px
  line-height: ${themeVal('type.base.line')};                                           // 24px

  > * {
    margin-bottom: ${multiply(themeVal('type.base.size'), themeVal('type.base.line'))}; // same as line-height
  }

  > *:last-child {
    margin-bottom: 0;
  }
`;

export default Prose;
