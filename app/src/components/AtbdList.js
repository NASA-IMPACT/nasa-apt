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

const AtbdList = (props) => {
  const { atbds } = props;
  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title } = atbd;
    return <div key={atbd_id}>{title}</div>;
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
      {atbdElements}
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
