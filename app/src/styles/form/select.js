import styled from 'styled-components';
import controlSkin from './control-skin';
import { themeVal } from '../utils/general';
import { multiply } from '../utils/math';

const FormSelect = styled.select.attrs(props => ({
  size: props.size || 'medium'
}))`
  ${controlSkin()}
  cursor: pointer;
  padding-right: ${multiply(themeVal('layout.space'), 2)};
  background-image: ${({ theme }) => `url('data:image/svg+xml;utf8,${encodeURIComponent(`<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="10px" height="5px" viewBox="0 0 10 5"><polygon fill="${theme.color.base}" points="5,5 0,0 10,0"/></svg>`)}');`}
  background-position: calc(100% - 0.75rem) center;
  background-repeat: no-repeat;

  /* IE specific */

  &::-ms-expand {
    display: none;
  }

  /* Firefox specific */

  @-moz-document url-prefix() {
    & {
      text-overflow: '';
      text-indent: -2px;
    }
  }

  :-moz-focusring {
    color: transparent;
    text-shadow: 0 0 0 ${themeVal('type.base.color')};
  }
`;

export default FormSelect;
