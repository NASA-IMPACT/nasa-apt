import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { StickyContainer, Sticky } from 'react-sticky';
import styled from 'styled-components/macro';
import { push } from 'connected-react-router';
import { createAtbd } from '../actions/actions';
import {
  atbdsedit,
  drafts,
  identifying_information
} from '../constants/routes';
import { themeVal } from '../styles/utils/general';
import { multiply, divide } from '../styles/utils/math';
import { VerticalDivider } from '../styles/divider';
import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';

import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageFilters,
  FilterItem,
  FilterLabel,
  InpageToolbar,
  InpageBody,
  InpageBodyInner
} from './common/Inpage';

import Dropdown, {
  DropTitle,
  DropMenu,
  DropMenuItem
} from './Dropdown';

const SearchButton = styled(Button)`
  &::before {
    ${collecticon('magnifier-right')}
  }
`;

const CreateButton = styled(Button)`
  &::before {
    ${collecticon('plus')}
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
  border-bottom: 1px solid ${themeVal('color.darkgray')};
  padding: ${themeVal('layout.space')};
`;

const AtbdHeaderCell = styled.th`
  color: ${themeVal('color.darkgray')};
  font-weight: normal;
  padding: ${themeVal('layout.space')} ${themeVal('layout.space')} 0;
  text-align: left;
  text-transform: uppercase;
`;

const AtbdPublishedState = styled.span`
  background-color: ${themeVal('color.darkgray')};
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
  color: ${themeVal('color.darkgray')};
`;

const EditIcon = styled.span`
  color: ${themeVal('color.link')};
  cursor: pointer;
  &::before {
    ${collecticon('pencil')};
  }
`;

const FilterTrigger = styled(Button)`
  &::after {
    ${collecticon('chevron-down--small')}
  }
`;

const AtbdList = (props) => {
  const { atbds, createAtbd: create } = props;
  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title, atbd_versions } = atbd;
    // We are using a default single version for the prototype.
    // This should be updated in the future.
    const { status } = atbd_versions[0];
    return (
      <AtbdRow scope="row" key={atbd_id}>
        <AtbdCell><AtbdPublishedState>{status}</AtbdPublishedState></AtbdCell>
        <AtbdCell>
          <AtbdTitle>{title}</AtbdTitle>
          { false && <AtbdVersion>Version 1.0</AtbdVersion> }
        </AtbdCell>
        <AtbdCell>2 hours ago</AtbdCell>
        <AtbdCell>Author Name</AtbdCell>
        <AtbdCell onClick={() => props.push(`/${atbdsedit}/${atbd_id}/${drafts}/1/${identifying_information}`)}><EditIcon /></AtbdCell>
      </AtbdRow>
    );
  });
  return (
    <Inpage>
      <StickyContainer>
        <Sticky>
          {stickyProps => (
            <InpageHeader style={stickyProps.style} isSticky={stickyProps.isSticky}>
              <InpageHeaderInner>
                <InpageHeadline>
                  <InpageTitle>Documents</InpageTitle>
                </InpageHeadline>
                <VerticalDivider />

                <InpageFilters>
                  <FilterItem>
                    <FilterLabel>Status</FilterLabel>
                    <Dropdown
                      alignment="left"
                      triggerElement={
                        <FilterTrigger variation="achromic-plain" title="Toggle menu options">All</FilterTrigger>
                      }
                    >
                      <DropTitle>Select status</DropTitle>
                      <DropMenu role="menu" selectable>
                        <li>
                          <DropMenuItem active>All</DropMenuItem>
                        </li>
                        <li>
                          <DropMenuItem>Published</DropMenuItem>
                        </li>
                        <li>
                          <DropMenuItem>Draft</DropMenuItem>
                        </li>
                      </DropMenu>
                    </Dropdown>
                  </FilterItem>

                  <FilterItem>
                    <FilterLabel>Authors</FilterLabel>
                    <Dropdown
                      alignment="left"
                      triggerElement={
                        <FilterTrigger variation="achromic-plain" title="Toggle menu options">All</FilterTrigger>
                      }
                    >
                      <DropTitle>Select author</DropTitle>
                      <DropMenu role="menu" selectable>
                        <li>
                          <DropMenuItem active>All</DropMenuItem>
                        </li>
                        <li>
                          <DropMenuItem>Lorem ipsum</DropMenuItem>
                        </li>
                      </DropMenu>
                    </Dropdown>
                  </FilterItem>

                  <FilterItem>
                    <FilterLabel>Sort</FilterLabel>
                    <Dropdown
                      alignment="left"
                      triggerElement={
                        <FilterTrigger variation="achromic-plain" title="Toggle menu options">Newest</FilterTrigger>
                      }
                    >
                      <DropTitle>Sort by</DropTitle>
                      <DropMenu role="menu" selectable>
                        <li>
                          <DropMenuItem active>Newest</DropMenuItem>
                          <DropMenuItem>Other</DropMenuItem>
                        </li>
                      </DropMenu>
                    </Dropdown>
                  </FilterItem>
                </InpageFilters>

                <InpageToolbar>
                  <SearchButton variation="achromic-plain" title="Search documents" disabled>Search</SearchButton>
                  <CreateButton variation="achromic-plain" title="Create new document" onClick={create}>Create</CreateButton>
                </InpageToolbar>

              </InpageHeaderInner>
            </InpageHeader>
          )}
        </Sticky>
        <InpageBody>
          <InpageBodyInner>
            <AtbdTable>
              <thead>
                <tr>
                  <AtbdHeaderCell scope="col" />
                  <AtbdHeaderCell scope="col" />
                  <AtbdHeaderCell scope="col">Last Edit</AtbdHeaderCell>
                  <AtbdHeaderCell scope="col">Authors</AtbdHeaderCell>
                </tr>
              </thead>
              <tbody>
                {atbdElements}
              </tbody>
            </AtbdTable>
          </InpageBodyInner>
        </InpageBody>
      </StickyContainer>
    </Inpage>
  );
};

AtbdList.propTypes = {
  atbds: PropTypes.arrayOf(PropTypes.shape({
    atbd_id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired
  })),
  push: PropTypes.func,
  createAtbd: PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  const { atbds } = state.application;
  return { atbds };
};

const mapDispatch = { push, createAtbd };

export default connect(mapStateToProps, mapDispatch)(AtbdList);
