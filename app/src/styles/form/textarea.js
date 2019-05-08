import styled from 'styled-components/macro';
import controlSkin from './control-skin';

const FormTextarea = styled.textarea.attrs(props => ({
  size: props.size || 'medium'
}))`
  ${controlSkin()}
  height: auto;
  min-height: 8rem;
  resize: none;
`;

export default FormTextarea;
