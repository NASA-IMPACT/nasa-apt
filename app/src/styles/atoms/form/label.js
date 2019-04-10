import styled, { css } from 'styled-components';
import { themeVal } from '../../utils/general';

const FormLabel = styled.label`
  grid-area: form-group-label;
  font-family: ${themeVal('type.base.family')};
  font-weight: ${themeVal('type.base.bold')};
  font-size: 1rem;
  line-height: 1.5;
`;

export default FormLabel;
