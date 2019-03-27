import React from 'react';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import Constrainer from '../../styles/atoms/constrainer';

const PageFoot = styled.footer`
  padding: ${themeVal('layout.space')};
  background-color: ${themeVal('color.shadow')};
  font-size: 0.875rem;
  line-height: 1rem;
`;

export const Inner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;

  * {
    opacity: 0.64;
  }
`;

class PageFooter extends React.PureComponent {
  render() {
    return (
      <PageFoot>
        <Inner>
          <p>Copyright goes here.</p>
        </Inner>
      </PageFoot>
    );
  }
}

export default PageFooter;
