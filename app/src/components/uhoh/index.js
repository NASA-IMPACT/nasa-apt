import React, { Component } from 'react';
import styled from 'styled-components';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import Constrainer from '../../styles/atoms/Constrainer';

const Inpage = styled.article`
  display: grid;
  height: 100%;
  grid-template-rows: auto 1fr;
`;

const InpageHeader = styled.header`
  ${antialiased()}
  background-color: ${themeVal('color.primary')};
  color: #FFF;
`;

const InpageHeaderInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
  padding: ${multiply(themeVal('layout.space'), 2)} ${themeVal('layout.space')} ${themeVal('layout.space')} ${themeVal('layout.space')};
`;

const InpageHeadline = styled.div`

`;

const InpageTitle = styled.h1`
  font-size: 1.25rem;
  line-height: 1;
  margin: 0;
`;

const InpageBody = styled.div`

`;

const InpageBodyInner = styled(Constrainer)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  align-items: center;
  padding: ${themeVal('layout.space')};
  height: 100%;
  text-align: center;
`;

class UhOh extends Component {
  render() {
    return (
      <Inpage>
        <InpageHeader>
          <InpageHeaderInner>
            <InpageHeadline>
              <InpageTitle>Page not found</InpageTitle>
            </InpageHeadline>
          </InpageHeaderInner>
        </InpageHeader>
        <InpageBody>
          <InpageBodyInner>
            <div>
              <p>We were not able to find the page you are looking for. It may have been archived or removed.</p>
              <p><a href='/' title='View page'>Visit the homepage</a>.</p>
            </div>
          </InpageBodyInner>
        </InpageBody>
      </Inpage>
    );
  }
}

export default UhOh;
