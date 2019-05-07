import { css } from 'styled-components/macro';
import { themeVal } from '../utils/general';
import { divide } from '../utils/math';
import { antialiased } from '../helpers';

export default () => css`
  /* Overrides for react-tooltip styles. */

  .__react_component_tooltip {
    ${antialiased};
    border-radius: ${themeVal('shape.rounded')};
    font-size: 0.875rem;
    line-height: 1.25rem;
    max-width: 16rem;
    padding: ${divide(themeVal('layout.space'), 2)} ${themeVal('layout.space')};

    &.type-primary {
      background: ${themeVal('color.base')};
      ${['top', 'bottom', 'left', 'right'].map(dir => css`
        &.place-${dir}::after {
          border-${dir}-color: ${themeVal('color.base')};
        }
      `)}
    }
  }
`;
