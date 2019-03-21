import { css } from 'styled-components';

const catalog = require('./catalog.json');

export const collecticonsFont = () => css`
  @font-face {
    font-family: "${catalog.name}";
    src: url(data:application/font-woff2;charset=utf-8;base64,${catalog.fonts.woff2}) format('woff2');
    font-weight: normal;
    font-style: normal;
  }
`;

export default function collecticon(name) {
  const calculatedName = `${catalog.className}-${name}`;
  const icon = catalog.icons.find(i => i.icon === calculatedName);
  const content = icon ? `\\${icon.charCode}` : 'n/a';
  return css`
    speak: none;
    font-family: "${catalog.name}";
    font-style: normal;
    font-weight: normal;
    font-variant: normal;
    text-transform: none;

    /* Better font rendering */
    text-rendering: auto;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    content: "${content}";
  `;
}
