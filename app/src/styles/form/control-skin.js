import { css } from 'styled-components';
import { rgba } from 'polished';
import { disabled } from '../helpers';
import { themeVal, stylizeFunction } from '../utils/general';
import { multiply, divide } from '../utils/math';

const _rgba = stylizeFunction(rgba);

const fontSizeMatrix = {
  small: '0.875rem',
  medium: '1rem',
  large: '1rem'
};

const lineHeightMatrix = {
  small: '1.25rem',
  medium: '1.5rem',
  large: '1.5rem'
};

const heightMatrix = {
  small: '1.5rem',
  medium: '2rem',
  large: '2.5rem'
};

const paddingMatrix = {
  small: '0.125rem 0.5rem',
  medium: '0.25rem 0.5rem',
  large: '0.5rem 0.75rem'
};

const controlSkin = () => css`
  appearance: none;
  display: flex;
  width: 100%;
  height: ${({ size }) => heightMatrix[size]};
  padding: ${({ size }) => paddingMatrix[size]};
  border-width: ${themeVal('layout.border')};
  border-style: solid;
  border-color: ${_rgba(themeVal('color.base'), 0.16)};
  border-radius: ${themeVal('shape.rounded')};
  background-color: #FFFFFF;
  font-family: inherit;
  font-size: ${({ size }) => fontSizeMatrix[size]};
  line-height: ${({ size }) => lineHeightMatrix[size]};
  color: ${themeVal('type.base.color')};
  transition: all 0.24s ease 0s;

  &::placeholder {
    opacity: 0.64;
  }

  &[disabled] {
    ${disabled()}
  }

  &[readonly] {
    cursor: text;
    color: rgba($base-font-color, 0.64);
  }

  &:hover {
    border-width: ${multiply(themeVal('layout.border'), 2)};
    border-color: ${_rgba(themeVal('color.base'), 0.32)};
  }

  &:focus,
  &:active {
    outline: 0;
    border-width: ${multiply(themeVal('layout.border'), 2)};
    border-color: ${themeVal('color.primary')};
  }

  ${({ invalid }) => invalid && css`
    border-width: ${multiply(themeVal('layout.border'), 2)};
    border-color: ${themeVal('color.danger')};

    &:hover,
    &:focus,
    &:active {
      border-color: ${themeVal('color.danger')};
    }
  `}
`;

export default controlSkin;
