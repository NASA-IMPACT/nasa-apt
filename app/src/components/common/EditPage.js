import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import Constrainer from '../../styles/atoms/constrainer';
import PageSubNav, {
  SubNavTitle,
  SubNavTagline,
  SubNavActions,
  SubNavAction
} from './PageSubNav';
import PageSection from './Page';
import { multiply } from '../../styles/utils/math';
import { themeVal } from '../../styles/utils/general';

export const EditorSection = styled.div`
  background-color: ${themeVal('color.lightgray')};
  padding: ${multiply(themeVal('layout.space'), 2)};
  margin-top: ${multiply(themeVal('layout.space'), 2)};
`;

export const EditorSectionTitle = styled.h4`
font-size: 1em;
font-weight: bold;
line-height: 2;
margin: 0;
`;

export const EditorLabel = styled.label`
  color: ${themeVal('color.darkgray')};
  display: block;
  font-size: 0.875rem;
  font-weight: lighter;
  line-height: 2;
  margin-bottom: ${multiply(themeVal('layout.space'), 2)};
  text-transform: uppercase;
`;

export const InputFormGroup = styled.form`
  margin-top: ${themeVal('layout.space')};
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
`;

export const InputLabel = styled.label`
  display: block
  font-weight: bold;
  margin: ${themeVal('layout.space')} 0 0;
  width: 32%;
`;

export const InputLabelFeedback = styled.span`
`;

export const SmallTextInput = styled.input`
  font-family: inherit;
  margin: ${multiply(themeVal('layout.space'), 0.5)} 0 0;
  padding: ${multiply(themeVal('layout.space'), 0.5)};
  width: 100%;
`;

export const InputSubmit = styled.input`
  background: #FFF;
  border: 1px solid $lightgray;
  box-shadow: ${themeVal('boxShadow.input')};
  font-size: 0.875rem;
  font-weight: bold;
  margin: ${themeVal('layout.space')} 0 0;
  padding: ${multiply(themeVal('layout.space'), 0.5)} ${multiply(themeVal('layout.space'), 2)};
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
