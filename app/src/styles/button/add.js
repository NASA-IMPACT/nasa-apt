import styled from 'styled-components/macro';
import Button from './button';
import collecticon from '../collecticons';

const AddBtn = styled(Button)`
  ::before {
    ${collecticon('plus')}
  }
`;
export default AddBtn;
