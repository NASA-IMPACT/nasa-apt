import { createGlobalStyle, css } from 'styled-components';
import { normalize } from 'polished';

import { themeVal } from './utils/general';
import { collecticonsFont } from './collecticons';

// Global styles for these components are included here for performance reasons.
// This way they're only rendered when absolutely needed.

const baseStyles = css`
  html {
    box-sizing: border-box;
    font-size: ${themeVal('type.base.root')};

    /* Changes the default tap highlight to be completely transparent in iOS. */
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
  }

  *,
  *::before,
  *::after {
    box-sizing: inherit;
  }

  body {
    background: ${themeVal('color.background')};
    color: ${themeVal('type.base.color')};
    font-size: ${themeVal('type.base.size')};
    line-height: ${themeVal('type.base.line')};
    /* stylelint-disable-next-line */
    font-family: ${themeVal('type.base.family')};
    font-weight: ${themeVal('type.base.weight')};
    font-style: ${themeVal('type.base.style')};
    min-width: ${themeVal('layout.min')};
  }

  a {
    cursor: pointer;
    color: ${themeVal('color.link')};
    text-decoration: none;
    transition: opacity 0.24s ease 0s;
  }

  a:visited {
    color: ${themeVal('color.link')};
  }

  a:hover {
    opacity: 0.64;
  }

  a:active {
    transform: translate(0, 1px);
  }

  /* Thether element */
  .tether-element {
    z-index: 1000;
  }

  #root {
    min-height: 100vh;
  }

  ul {
    list-style: none;
    margin: 0;
    margin-block-start: 0;
    margin-block-end: 0;
  }
`;

export default createGlobalStyle`
  ${normalize()}
  ${collecticonsFont()}
  ${baseStyles}
`;
