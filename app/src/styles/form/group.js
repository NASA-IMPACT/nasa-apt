import styled from 'styled-components';
import { themeVal } from '../utils/general';

const FormGroup = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto;
  grid-template-areas:
    "form-group-label form-group-toolbar"
    "form-group-body form-group-body";
  }
  grid-gap: ${themeVal('layout.space')};

  > * {
    grid-column-start: 1;
    grid-column-end: -1;
  }
`;

export default FormGroup;
