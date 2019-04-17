import styled from 'styled-components';
import { rgba } from 'polished';
import { themeVal, stylizeFunction } from '../utils/general';
import { divide } from '../utils/math';
import { headingAlt } from '../type/heading';

const _rgba = stylizeFunction(rgba);

const FormLegend = styled.legend`
  ${headingAlt()}
  display: flex;
  align-items: center;
  width: 100%;
  color: ${_rgba(themeVal('type.base.color'), 0.64)};
  font-size: 0.875rem;
  line-height: 1rem;
  border: 0;
  padding: ${divide(themeVal('layout.border'), 4)} 0;
`;

export default FormLegend;
