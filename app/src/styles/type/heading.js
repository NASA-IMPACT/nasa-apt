import styled, { css } from 'styled-components';
import { themeVal } from '../utils/general';

const sizeMapping = {
  small: '0.875rem',
  medium: '1rem',
  large: '1.125rem',
  xlarge: '1.25rem'
};

const lineHeightMapping = {
  small: '1rem',
  medium: '1.25rem',
  large: '1.5rem',
  xlarge: '1.75rem'
};

const getHeadingColor = ({ variation, theme }) => {
  if (variation === 'base') return theme.type.base.color;
  if (variation === 'primary') return theme.collor.primary;
  if (variation === 'secondary') return theme.collor.secondary;

  return 'inherit';
};

const Heading = styled.h1`
  font-family: ${themeVal('type.heading.family')};
  font-weight: ${themeVal('type.heading.weight')};
  text-transform: uppercase;

  /* Size and line-height attribute */
  ${({ size }) => `
    font-size: ${sizeMapping[size]};
    line-height: ${lineHeightMapping[size]};
  `}

  /* Colors */
  color:
    ${getHeadingColor};
`;

Heading.defaultProps = {
  size: 'medium'
};

export default Heading;

export const headingAlt = () => css`
  font-feature-settings: "pnum" 0; /* Use proportional numbers */
  font-family: ${themeVal('type.heading.family')};
  font-weight: ${themeVal('type.heading.light')};
  text-transform: uppercase;
`;
