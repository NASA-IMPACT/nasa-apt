import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import styled from 'styled-components';
import { themeVal } from '../styles/utils/general';
import { multiply, divide } from '../styles/utils/math';
import collecticon from '../styles/collecticons';
import PageSubNav, {
  SubNavTitle,
  SubNavFilter,
  SubNavActions,
  SubNavAction
} from './common/PageSubNav';
import Dropdown from './Dropdown';
import { Inner } from './common/Page';

const Separator = styled.span`
  border-right: 1px solid ${themeVal('color.lightgray')};
  padding-right: ${multiply(themeVal('layout.space'), 2)};
  margin-right: ${multiply(themeVal('layout.space'), 2)};
`;

const DropdownTrigger = styled.a`
  color: #FFF;
  font-weight: bold;
  padding: ${themeVal('layout.space')};
  &::after {
    margin-left: ${divide(themeVal('layout.space'), 2)};
    ${collecticon('chevron-down--small')};
  }
`;

const DropdownList = styled.ul`
  background-color: ${themeVal('color.background')};
  border-radius: ${divide(themeVal('layout.space'), 4)};
  box-shadow: 0 0 0 1px rgba(0,0,0,.08), 0 4px 16px 2px rgba(0,0,0,.08);

  padding: ${divide(themeVal('layout.space'), 2)} 0;
  text-align: center;
`;

const DropdownItem = styled.li`
  background-color: ${themeVal('color.background')};
  cursor: pointer;
  padding: ${divide(themeVal('layout.space'), 4)} ${themeVal('layout.space')};
  transition: background-color .16s ease;
  &:hover {
    background-color: ${themeVal('color.shadow')};
  }
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
  }))
};

const mapStateToProps = (state) => {
  const { atbds } = state.application;
  return { atbds };
};

export default connect(mapStateToProps)(AtbdList);
