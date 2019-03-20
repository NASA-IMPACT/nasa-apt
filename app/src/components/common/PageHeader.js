import React from 'react';
import { PropTypes as T } from 'prop-types';
import styled, { css } from 'styled-components';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';

const PageHead = styled.header`
  ${antialiased()}
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  padding: ${themeVal('layout.space')};
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

const PageHeadline = styled.div`

`;

const PageTitle = styled.h1`
  font-size: 1.5rem;
  text-transform: uppercase;
  line-height: 1;
  margin: 0;
`;

const PageNav = styled.nav`
  display: flex;
  margin: 0 0 0 auto;
`;

const GlobalMenu = styled.ul`
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  margin: 0;
  list-style: none;

  > * {
    margin: 0 0 0 ${themeVal('layout.space')};
  }
`;


class PageHeader extends React.PureComponent {
  render () {
    return (
      <PageHead>
        <PageHeadline>
          <PageTitle>NASA APT</PageTitle>
        </PageHeadline>
        <PageNav>
          <GlobalMenu>
            <li>Item A</li>
            <li>Item B</li>
            <li>Item C</li>
            <li>Item D</li>
          </GlobalMenu>
        </PageNav>
      </PageHead>
    );
  }
}

export default PageHeader;