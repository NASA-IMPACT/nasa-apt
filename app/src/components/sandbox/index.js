import React, { Component } from 'react';

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
