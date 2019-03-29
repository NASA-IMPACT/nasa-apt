import React, { Component } from 'react';
import styled from 'styled-components';
import { antialiased } from '../../styles/helpers';
import { themeVal } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import Constrainer from '../../styles/atoms/Constrainer';

import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageBody,
  InpageBodyInner
} from '../common/Inpage';

class Sandbox extends Component {
  render() {
    return (
      <Inpage>
        <InpageHeader>
          <InpageHeaderInner>
            <InpageHeadline>
              <InpageTitle>Sandbox</InpageTitle>
            </InpageHeadline>
          </InpageHeaderInner>
        </InpageHeader>
        <InpageBody>
          <InpageBodyInner>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin imperdiet diam magna, id pulvinar libero scelerisque et. Quisque sollicitudin massa nec arcu dapibus mollis.</p>
          </InpageBodyInner>
        </InpageBody>
      </Inpage>
    );
  }
}

export default Sandbox;
