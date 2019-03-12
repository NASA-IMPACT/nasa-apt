import styled from 'styled-components';
import collecticon from '../styles/collecticons';

export const Button = styled('span')`
  cursor: pointer;
`;

export const Icon = styled.span`
  font-size: 1rem;
  &::after {
    ${collecticon('plus')}
  }
`;

export const Menu = styled('div')`
  & > * {
    display: inline-block;
  }

  & > * + * {
    margin-left: 15px;
  }
`;

export const Toolbar = styled(Menu)`
  position: relative;
  padding: 1px 18px 17px;
  margin: 0 -20px;
  border-bottom: 2px solid #eee;
  margin-bottom: 20px;
`;
