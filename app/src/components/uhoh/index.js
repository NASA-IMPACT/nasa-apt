import React, { Component } from 'react';
import styled from 'styled-components';

import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageBody,
  InpageBodyInner
} from '../common/Inpage';

const InpageBodyInnerUhOh = styled(InpageBodyInner)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: center;
  align-items: center;
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
          <InpageBodyInnerUhOh>
            <div>
              <p>We were not able to find the page you are looking for. It may have been archived or removed.</p>
              <p>hello this is <a href="/" title="View page">Visit the homepage</a>.</p>
            </div>
          </InpageBodyInnerUhOh>
        </InpageBody>
      </Inpage>
    );
  }
}

export default UhOh;
