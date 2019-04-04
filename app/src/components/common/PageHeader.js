import React from 'react';
import styled from 'styled-components';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import Constrainer from '../../styles/atoms/constrainer';

const PageHead = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

const PageHeadInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
`;

const PageHeadline = styled.div`

`;

const PageTitle = styled.h1`
  font-size: 1.5rem;
  line-height: 1;
  text-transform: uppercase;
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
    margin: 0 0 0 ${multiply(themeVal('layout.space'), 2)};
  }

  a {
    font-weight: ${themeVal('type.base.bold')};
    color: inherit;
  }
`;

class PageHeader extends React.PureComponent {
  render() {
    return (
      <PageHead>
        <PageHeadInner>
          <PageHeadline>
            <PageTitle>NASA APT</PageTitle>
          </PageHeadline>
          <PageNav>
            <GlobalMenu>
              <li><a href="/" title="View">Dashboard</a></li>
              <li><a href="/atbds" title="View">Documents</a></li>
              <li><a href="/help" title="View">Help</a></li>
              <li><a href="/about" title="View">About</a></li>
            </GlobalMenu>
          </PageNav>
        </PageHeadInner>
      </PageHead>
    );
  }
}

export default PageHeader;
