import React from 'react';
import styled from 'styled-components';
import { Link, withRouter, NavLink } from 'react-router-dom';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import { Inner } from './Page';


const PageHead = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

const PageHeadline = styled.div`

`;

const PageTitle = styled.h1`
  font-size: 1.5rem;
  line-height: 1;
  text-transform: uppercase;
  margin: 0;

  a {
    color: inherit;
    display: block;
  }
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
    position: relative;
    font-weight: ${themeVal('type.base.bold')};
    color: inherit;
  }

  .active::before {
    position: absolute;
    top: 100%;
    width: 2rem;
    height: 0.125rem;
    background: #FFFFFF;
    content: '';
  }
`;

class PageHeader extends React.PureComponent {
  render() {
    return (
      <PageHead>
        <Inner>
          <PageHeadline>
            <PageTitle>
              <Link to="/" title="Go to Homepage">NASA APT</Link>
            </PageTitle>
          </PageHeadline>
          <PageNav>
            <GlobalMenu>
              <li><NavLink exact to="/" title="View page"><span>Dashboard</span></NavLink></li>
              <li><NavLink exact to="/atbds" title="View page"><span>Documents</span></NavLink></li>
              <li><NavLink exact to="/help" title="View page"><span>Help</span></NavLink></li>
              <li><NavLink exact to="/about" title="View page"><span>About</span></NavLink></li>
            </GlobalMenu>
          </PageNav>
        </Inner>
      </PageHead>
    );
  }
}

export default withRouter(PageHeader);
