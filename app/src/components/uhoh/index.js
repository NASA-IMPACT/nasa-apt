import React, { Component } from 'react';
import styled from 'styled-components';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import Constrainer from '../../styles/atoms/Constrainer';

const InpageHeaderInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
  padding: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

const Inpage = styled.article`

`;

const InpageHeader = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

const InpageTitle = styled.h1`
  font-size: 1.25rem;
  line-height: 1;
  margin: 0;
`;

const InpageBody = styled.div`

`;

const InpageBodyInner = styled(Constrainer)`
  padding: ${themeVal('layout.space')};
`;

class UhOh extends Component {
  render() {
    return (
      <Inpage>
        <InpageHeader>
          <InpageHeaderInner>
            <InpageTitle as="h1" variation="base">Page not found</InpageTitle>
          </InpageHeaderInner>
        </InpageHeader>
        <InpageBody>
          <InpageBodyInner>
            <p>We were not able to find the page you are looking for. It may have been archived or removed.</p>
            <p><a href='/' title='View page'>Visit the homepage</a>.</p>
          </InpageBodyInner>
        </InpageBody>
      </Inpage>
    );
  }
}

export default UhOh;
