import styled from 'styled-components';
import { rgba } from 'polished';

import { truncated, antialiased } from '../../styles/helpers';
import { themeVal, stylizeFunction } from '../../styles/utils/general';
import { multiply, divide } from '../../styles/utils/math';
import { headingAlt } from '../../styles/type/heading';
import Constrainer from '../../styles/constrainer';

const _rgba = stylizeFunction(rgba);

export const Inpage = styled.article`
  display: grid;
  height: 100%;
  grid-template-rows: auto 1fr;
`;

export const InpageHeader = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

export const InpageHeaderInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
  min-height: 5rem;
`;

export const InpageHeadline = styled.div`
  display: flex;
  flex-flow: column;
`;

export const InpageTitle = styled.h1`
  ${truncated()}
  font-size: 1.25rem;
  line-height: 2rem;
  max-width: 24rem;
  margin: 0;
`;

export const InpageTagline = styled.p`
  ${headingAlt()}
  order: -1;
  font-size: 0.875rem;
  line-height: 1rem;
  color: ${_rgba('#FFFFFF', 0.64)};
`;

export const InpageFilters = styled.div`
  display: flex;
  flex-flow: row nowrap;
`;

export const FilterItem = styled.div`
  display: flex;
  flex-flow: row nowrap;
  line-height: 2rem;
  margin: 0 ${multiply(themeVal('layout.space'), 2)} 0 0;

  > * {
    display: inline-flex;
  }
`;

export const FilterLabel = styled.h6`
  ${headingAlt()}
  font-size: 0.875rem;
  color: ${_rgba('#FFFFFF', 0.64)};
  margin-right: 0.5rem;
`;

export const InpageToolbar = styled.div`
  display: flex;
  flex-flow: row nowrap;
  margin: 0 0 0 auto;
  line-height: 2rem;

  > * {
    margin: 0 0 0 ${divide(themeVal('layout.space'), 2)};
  }

  a {
    display: inline-flex;
    font-weight: ${themeVal('type.base.bold')};
    color: inherit;
  }

  > button:last-child {
    margin-right: -1rem;
  }

  button + button {
    margin-left: 0;
  }
`;

export const InpageBody = styled.div`

`;

export const InpageBodyInner = styled(Constrainer)`
  padding-top: ${multiply(themeVal('layout.space'), 4)};
  padding-bottom: ${multiply(themeVal('layout.space'), 4)};
`;
