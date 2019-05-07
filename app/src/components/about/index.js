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
import Prose from '../../styles/type/prose';

class About extends Component {
  render() {
    return (
      <Inpage>
        <InpageHeader>
          <InpageHeaderInner>
            <InpageHeadline>
              <InpageTitle>About</InpageTitle>
            </InpageHeadline>
          </InpageHeaderInner>
        </InpageHeader>
        <InpageBody>
          <InpageBodyInner>
            <Prose>
              <p>
                This is the <strong>Algorithm Publication Tool</strong> prototype.<br />
                We have endeavored to make it as easy as possible to create new ATBDs, and welcome all feedback.
              </p>
              <p>Please feel free to <a href="mailto:alyssa@developmentseed.org?Subject=APT Prototype Feedback" target="_top">send us an e-mail</a>.</p>
            </Prose>
          </InpageBodyInner>
        </InpageBody>
      </Inpage>
    );
  }
}

export default About;
