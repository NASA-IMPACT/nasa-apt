import styled from 'styled-components';
import { themeVal } from '../../utils/general';

const FormLabel = styled.label`
  grid-area: form-group-label;
  display: inline-flex;
  font-family: ${themeVal('type.base.family')};
  font-weight: ${themeVal('type.base.bold')};
  font-size: 1rem;
  line-height: 1.5;

  &[for] {
    cursor: pointer;
  }
`;

export default FormLabel;
