import styled from 'styled-components';
import { rgba } from 'polished';
import { themeVal, stylizeFunction } from '../utils/general';

const _rgba = stylizeFunction(rgba);

const FormHelp = styled.p`
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: ${_rgba(themeVal('color.base'), 0.48)};
`;

export default FormHelp;
