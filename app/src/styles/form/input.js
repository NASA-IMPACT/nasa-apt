import styled from 'styled-components';
import controlSkin from './control-skin';

const FormInput = styled.input.attrs(props => ({
  size: props.size || 'medium'
}))`
  ${controlSkin()}
`;

export default FormInput;
