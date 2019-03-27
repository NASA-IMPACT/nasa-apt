import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Constrainer from '../../styles/atoms/constrainer';
import PageSubNav, {
  SubNavTitle,
  SubNavTagline,
  SubNavFilter,
  SubNavActions,
  SubNavAction
} from './PageSubNav';
import PageSection, { Inner } from './Page';
import { multiply } from '../../styles/utils/math';
import { themeVal } from '../../styles/utils/general';

export const EditorSection = styled.div`
  background-color: ${themeVal('color.lightgray')};
  padding: ${multiply(themeVal('layout.space'), 2)};
  margin-top: ${multiply(themeVal('layout.space'), 2)};
`;

export const EditorLabel = styled.label`
  font-weight: bold;
  line-height: 2;
`;

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
      <PageSection>
        <Constrainer>
          { children }
        </Constrainer>
      </PageSection>
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
