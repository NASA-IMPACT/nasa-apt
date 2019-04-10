import { css } from 'styled-components';
import { themeVal } from '../utils/general';

export default () => css`
  /* Overrides for react-tooltip styles. */

  .__react_component_tooltip {
    border-radius: 0;
    font-size: 0.875rem;

    &.type-primary {
      background: ${themeVal('colors.primaryDark')};
      ${['top', 'bottom', 'left', 'right'].map(dir => css`
        &.place-${dir}::after {
          border-${dir}-color: ${themeVal('colors.primaryDark')};
        }
      `)}
    }
  }
`;
