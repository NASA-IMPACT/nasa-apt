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
import { visuallyHidden, truncated } from '../styles/helpers';
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

import {
  Table,
  TableHead,
  TableBody,
  TableTr,
  TableHeadTh,
  TableBodyTh,
  TableTd
} from '../styles/table';

import AtbdPreview from './AtbdPreview';

const SearchButton = styled(Button)`
  &::before {
    ${collecticon('magnifier-right')};
  }
`;

const CreateButton = styled(Button)`
  &::before {
    ${collecticon('plus')};
  }
`;

const DocTable = styled(Table)`
  table-layout: fixed;

  thead {
    white-space;
  }
`;

const DocTableHeadThStatus = styled(TableHeadTh)`

`;

const DocTableHeadThTitle = styled(TableHeadTh)`

`;

const DocTableHeadThTime = styled(TableHeadTh)`

`;

const DocTableHeadThAuthors = styled(TableHeadTh)`

`;

const DocTableHeadThActions = styled(TableHeadTh)`
  > span {
    ${visuallyHidden};
  }
`;

const DocTableBodyTdStatus = styled(TableTd)`
  white-space: nowrap;
`;

const DocTableBodyThTitle = styled(TableBodyTh)`
  width: auto;
`;

const DocTableBodyTdTime = styled(TableTd)`
  white-space: nowrap;
`;

const DocTableBodyTdAuthors = styled(TableTd)`
  > span {
    ${truncated};
    display: block;
    max-width: 8rem;
  }
`;

const DocTableBodyTdActions = styled(TableTd)`
  text-align: right;
  white-space: nowrap;

  > *:not(:first-child) {
    margin-left: 0.5rem;
  }
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
  const {
    atbds,
    createAtbd: create,
  } = props;

  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title, atbd_versions } = atbd;
    const { status } = atbd_versions[0];
    return (
      <TableTr key={atbd_id}>
        <DocTableBodyTdStatus><AtbdPublishedState>{status}</AtbdPublishedState></DocTableBodyTdStatus>
        <DocTableBodyThTitle scope="row">
          <strong>{title}</strong>
          { false && <AtbdVersion>Version 1.0</AtbdVersion> }
        </DocTableBodyThTitle>
        <DocTableBodyTdTime><span>2 hours ago</span></DocTableBodyTdTime>
        <DocTableBodyTdAuthors><span>Author Name</span></DocTableBodyTdAuthors>
        <DocTableBodyTdActions>
          <AtbdPreview
            atbd_id={atbd_id}
            atbd_version={1}
          />
          <a href="#" title="Publish document">Publish</a>
          <a href="#" title="Edit document" onClick={() => props.push(`/${atbdsedit}/${atbd_id}/${drafts}/1/${identifying_information}`)}>Edit</a>
        </DocTableBodyTdActions>
      </TableTr>
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
            <DocTable>
              <TableHead>
                <TableTr>
                  <DocTableHeadThStatus scope="col"><span>Status</span></DocTableHeadThStatus>
                  <DocTableHeadThTitle scope="col"><span>Title</span></DocTableHeadThTitle>
                  <DocTableHeadThTime scope="col"><span>Last Edit</span></DocTableHeadThTime>
                  <DocTableHeadThAuthors scope="col"><span>Authors</span></DocTableHeadThAuthors>
                  <DocTableHeadThActions scope="col"><span>Actions</span></DocTableHeadThActions>
                </TableTr>
              </TableHead>
              <TableBody>
                {atbdElements}
              </TableBody>
            </DocTable>
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
