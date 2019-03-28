import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import { Inner } from './Page';

const SubNav = styled.div`
  background-color: ${themeVal('color.primary')};
  color: #FFF;
  padding: ${multiply(themeVal('layout.space'), 3)} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

export const SubNavTitle = styled.h2`
  font-size: 1.25rem;
  line-height: 1;
  margin: 0;
`;

export const SubNavTagline = styled.span`
  color: ${themeVal('color.background')};
  display: block;
  font-size: 0.875rem;
  font-weight: lighter;
  line-height: 1.4;
  margin: 0;
  text-transform: uppercase;
`;

export const SubNavFilter = styled.div`
  margin-right: ${themeVal('layout.space')};
`;

export const SubNavActions = styled.ul`
  display: flex;
  margin: 0 0 0 auto;
`;

export const SubNavAction = styled.li`
  margin-left: ${themeVal('layout.space')};
`;

const SubNavContainer = styled(Inner)`
  align-items: flex-end;
`;

const PageSubNav = (props) => {
  const {
    children
  } = props;

  return (
    <SubNav>
      <SubNavContainer>
        {children}
      </SubNavContainer>
    </SubNav>
  );
};

PageSubNav.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ])
};

export default PageSubNav;
