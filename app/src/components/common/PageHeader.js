import React from 'react';
import { PropTypes as T } from 'prop-types';
import styled, { css } from 'styled-components';
import { themeVal } from '../../styles/utils/general';

const Header = styled.header`
  padding: ${themeVal('layout.space')};
  background-color: ${themeVal('color.shadow')};
`;

class PageHeader extends React.PureComponent {
  render () {
    return (
      <Header>
        <h1>NASA APT</h1>
      </Header>
    );
  }
}

export default PageHeader;
