import styled from 'styled-components';

const EditorImage = styled.img`
  display: block;
  max-width: 100%;
  max-height: 20em;
  box-shadow: ${props => props.isFocused ? '0 0 0 2px blue' : 'none'};
`;

export default EditorImage;
