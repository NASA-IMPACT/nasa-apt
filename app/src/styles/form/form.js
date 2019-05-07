import styled from 'styled-components/macro';
import { themeVal } from '../utils/general';

const Form = styled.form`
  display: grid;
  grid-template-rows: auto;
  grid-gap: ${themeVal('layout.space')};
`;

export default Form;
