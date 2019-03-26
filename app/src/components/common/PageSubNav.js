import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import { Inner } from './PageHeader';

const SubNav = styled.div`
  background-color: ${themeVal('color.primary')};
  color: #FFF;
  padding-top: ${multiply(themeVal('layout.space'), 3)};
  padding-bottom: ${themeVal('layout.space')};
`;

export const SubNavTitle = styled.h2`
  font-size: 1.25rem;
  line-height: 1;
  margin: 0;
`;

export const SubNavFilter = styled.div`
`;

export const SubNavActions = styled.ul`
  display: flex;
  margin: 0 0 0 auto;
`;

export const SubNavAction = styled.li`
`;

const PageSubNav = (props) => {
  const {
    children
  } = props;

  return (
    <SubNav>
      <Inner>
        {children}
      </Inner>
    </SubNav>
  );
};

PageSubNav.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ])
};

export default PageSubNav


