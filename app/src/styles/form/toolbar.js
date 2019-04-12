import styled from 'styled-components';

const FormToolbar = styled.div`
  grid-area: form-group-toolbar;
  display: flex;
  flex-flow: row nowrap;

  > *:not[:first-child] {
    margin-left: 0.25rem;
  }
`;

export default FormToolbar;
