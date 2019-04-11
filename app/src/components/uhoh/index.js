import React, { Component } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageBody,
  InpageBodyInner
} from '../common/Inpage';
import Prose from '../../styles/molecules/type/prose';

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
            <Prose>
              <p>We were not able to find the page you are looking for. It may have been archived or removed.</p>
              <p>Please <Link to="/" title="View page">visit the homepage</Link>.</p>
            </Prose>
          </InpageBodyInnerUhOh>
        </InpageBody>
      </Inpage>
    );
  }
}

export default UhOh;
