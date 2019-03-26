import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import PageSubNav, {
  SubNavTitle,
  SubNavTagline,
  SubNavFilter,
  SubNavActions,
  SubNavAction
} from './PageSubNav';

const EditPage = (props) => {
  const { children, title } = props;
  return (
    <Fragment>
      <PageSubNav>
        <SubNavTitle>
          <SubNavTagline>Editing Document</SubNavTagline>
          { title }
        </SubNavTitle>

        <SubNavActions>
          <SubNavAction>Search</SubNavAction>
          <SubNavAction>Create</SubNavAction>
        </SubNavActions>
      </PageSubNav>
      { children }
    </Fragment>
  );
};

EditPage.propTypes = {
  title: PropTypes.string,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ])
};

export default EditPage;
