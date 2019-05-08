import styled from 'styled-components/macro';
import { rgba } from 'polished';
import { themeVal, stylizeFunction } from './utils/general';
import { divide } from './utils/math';
import { headingAlt } from './type/heading';

const _rgba = stylizeFunction(rgba);

export const Table = styled.table`
  width: 100%;
  max-width: 100%;
  padding: ${themeVal('layout.space')};
`;

export const TableHead = styled.thead`

`;

export const TableBody = styled.tbody`

`;

export const TableTr = styled.tr`

`;

export const TableHeadTh = styled.th`
  ${headingAlt};
  color: ${_rgba(themeVal('color.base'), 0.64)};
  padding: ${divide(themeVal('layout.space'), 2)};
  font-size: 0.875rem;
  line-height: 1.25rem;
  vertical-align: bottom;
  text-align: left;

  &:first-child {
    padding-left: ${themeVal('layout.space')};
  }

  &:last-child {
    padding-right: ${themeVal('layout.space')};
  }

  a {
    display: inline-flex;
  }

  a,
  a:visited,
  a:hover {
    color: inherit;
  }
`;

export const TableBodyTh = styled.th`
  padding: ${divide(themeVal('layout.space'), 2)};
  border-bottom: ${themeVal('layout.border')} solid ${themeVal('color.shadow')};
  vertical-align: top;
  text-align: left;

  &:first-child {
    padding-left: ${themeVal('layout.space')};
  }

  &:last-child {
    padding-right: ${themeVal('layout.space')};
  }
`;

export const TableTd = styled.td`
  padding: ${divide(themeVal('layout.space'), 2)};
  border-bottom: ${themeVal('layout.border')} solid ${themeVal('color.shadow')};
  vertical-align: top;
  text-align: left;

  &:first-child {
    padding-left: ${themeVal('layout.space')};
  }

  &:last-child {
    padding-right: ${themeVal('layout.space')};
  }
`;
