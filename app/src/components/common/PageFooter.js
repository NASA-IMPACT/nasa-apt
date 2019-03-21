import React from 'react';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';

const PageFoot = styled.footer`
  padding: ${themeVal('layout.space')};
  background-color: ${themeVal('color.shadow')};
`;

class PageFooter extends React.PureComponent {
  render () {
    return (
      <PageFoot>
        <p>Copyright goes here.</p>
      </PageFoot>
    );
  }
}

export default PageFooter;
