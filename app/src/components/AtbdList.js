import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import styled from 'styled-components';
import { push } from 'connected-react-router';
import {
  atbdsedit,
  contacts
} from '../constants/routes';
import { themeVal } from '../styles/utils/general';
import { multiply, divide } from '../styles/utils/math';
import collecticon from '../styles/collecticons';
import PageSubNav, {
  SubNavTitle,
  SubNavFilter,
  SubNavActions,
  SubNavAction
} from './common/PageSubNav';
import Dropdown, {
  DropdownTrigger,
  DropdownList,
  DropdownItem
} from './Dropdown';
import { Inner } from './common/Page';

const Separator = styled.span`
  border-right: 1px solid ${themeVal('color.lightgray')};
  padding-right: ${multiply(themeVal('layout.space'), 2)};
  margin-right: ${multiply(themeVal('layout.space'), 2)};
`;

const AtbdTable = styled.table`
  border-collapse: collapse;
  padding: ${themeVal('layout.space')};
  width: 100%;
`;

const AtbdRow = styled.tr`
`;

const AtbdCell = styled.td`
  border-bottom: 1px solid ${themeVal('color.lightgray')};
  padding: ${themeVal('layout.space')};
`;

const AtbdHeaderCell = styled.th`
  color: ${themeVal('color.lightgray')};
  font-weight: normal;
  padding: ${themeVal('layout.space')} ${themeVal('layout.space')} 0;
  text-align: left;
  text-transform: uppercase;
`;

const AtbdPublishedState = styled.span`
  background-color: ${themeVal('color.lightgray')};
  border-radius: ${multiply(themeVal('layout.space'), 2)};
  color: ${themeVal('color.surface')};
  display: inline-block;
  padding: ${divide(themeVal('layout.space'), 2)} 0;
  text-align: center;
  width: 100%;
`;

const AtbdTitle = styled.h5`
  font-size: 1em;
  line-height: 1.4;
  margin: 0;
`;

const AtbdVersion = styled.span`
  text-transform: uppercase;
  color: ${themeVal('color.lightgray')};
`;

const EditIcon = styled.span`
  color: ${themeVal('color.link')};
  cursor: pointer;
  &::before {
    ${collecticon('pencil')};
  }
`;

const AtbdList = (props) => {
  const { atbds } = props;
  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title } = atbd;
    return (
      <AtbdRow scope="row" key={atbd_id}>
        <AtbdCell><AtbdPublishedState>Status</AtbdPublishedState></AtbdCell>
        <AtbdCell>
          <AtbdTitle>{title}</AtbdTitle>
          { false && <AtbdVersion>Version 1.0</AtbdVersion> }
        </AtbdCell>
        <AtbdCell>2 hours ago</AtbdCell>
        <AtbdCell>Author Name</AtbdCell>
        <AtbdCell>Topic</AtbdCell>
        <AtbdCell onClick={() => props.push(`/${atbdsedit}/${atbd_id}/${contacts}`)}><EditIcon /></AtbdCell>
      </AtbdRow>
    );
  });
  return (
    <Fragment>
      <PageSubNav>
        <Separator><SubNavTitle>Documents</SubNavTitle></Separator>

        <SubNavFilter>
          Status
          <Dropdown
            triggerText="All"
            triggerTitle="Toggle menu options"
            triggerElement={DropdownTrigger}
          >
            <DropdownList role="menu">
              <DropdownItem>All</DropdownItem>
              <DropdownItem>Published</DropdownItem>
              <DropdownItem>Draft</DropdownItem>
            </DropdownList>
          </Dropdown>
        </SubNavFilter>

        <SubNavFilter>
          Authors
          <Dropdown
            triggerText="All"
            triggerTitle="Toggle menu options"
            triggerElement={DropdownTrigger}
          >
            <DropdownList role="menu">
              <DropdownItem>All</DropdownItem>
            </DropdownList>
          </Dropdown>
        </SubNavFilter>

        <SubNavFilter>
          Topics
          <Dropdown
            triggerText="All"
            triggerTitle="Toggle menu options"
            triggerElement={DropdownTrigger}
          >
            <DropdownList role="menu">
              <DropdownItem>All</DropdownItem>
            </DropdownList>
          </Dropdown>
        </SubNavFilter>

        <SubNavFilter>
          Sort
          <Dropdown
            triggerText="Newest"
            triggerTitle="Toggle menu options"
            triggerElement={DropdownTrigger}
          >
            <DropdownList role="menu">
              <DropdownItem>Newest</DropdownItem>
            </DropdownList>
          </Dropdown>
        </SubNavFilter>

        <SubNavActions>
          <SubNavAction>Search</SubNavAction>
          <SubNavAction>Create</SubNavAction>
        </SubNavActions>
      </PageSubNav>

      <Inner>
        <AtbdTable>
          <thead>
            <tr>
              <AtbdHeaderCell scope="col" />
              <AtbdHeaderCell scope="col" />
              <AtbdHeaderCell scope="col">Last Edit</AtbdHeaderCell>
              <AtbdHeaderCell scope="col">Authors</AtbdHeaderCell>
              <AtbdHeaderCell scope="col">Topics</AtbdHeaderCell>
            </tr>
          </thead>
          <tbody>
            {atbdElements}
          </tbody>
        </AtbdTable>
      </Inner>
    </Fragment>
  );
};

AtbdList.propTypes = {
  atbds: PropTypes.arrayOf(PropTypes.shape({
    atbd_id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired
  })),
  push: PropTypes.func
};

const mapStateToProps = (state) => {
  const { atbds } = state.application;
  return { atbds };
};

const mapDispatch = { push };

export default connect(mapStateToProps, mapDispatch)(AtbdList);
