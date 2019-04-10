import styled, { css } from 'styled-components';
import { rgba } from 'polished';
import { themeVal } from '../../utils/general';

const FormHelp = styled.p`
  text-align: right;
  font-size: 0.875rem;
  line-height: 1.25rem;
  color: rgba(theme.color.base, 0.48);
`;

export default FormHelp;
