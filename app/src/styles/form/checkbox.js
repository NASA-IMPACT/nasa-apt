import React from 'react';
import T from 'prop-types';
import styled, { css } from 'styled-components';
import { rgba } from 'polished';

import { visuallyHidden } from '../helpers';
import { themeVal, stylizeFunction } from '../utils/general';
import { divide } from '../utils/math';
import collecticon from '../collecticons';

const _rgba = stylizeFunction(rgba);

/**
 * Renders a FormCheckbox component.
 *
 * @param {string} name (html prop) name to be used as `name` and `id` prop
 *                      of the checkbox.
 * @param {string} title (html prop) Label's title attribute
 * @param {boolean} checked Whether or not the FormSwitch is checked
 * @param {func} onChange Change callbalck for the FormSwitch
 * @param {node} children Content of the label
 * @param {string} textPlacement Where to position the text. `left` or `right`
 *                  of the control.
 */
const FormCheckboxElement = props => {
  const {
    children,
    name,
    title,
    checked,
    onChange,
    className,
    textPlacement
  } = props;

  return (
    <label htmlFor={name} className={className} title={title}>
      <input
        type='checkbox'
        name={name}
        id={name}
        value='On'
        checked={checked}
        onChange={onChange}
      />
      {textPlacement === 'right' && <FormOptionUi />}
      <FormOptionText>{children}</FormOptionText>
      {textPlacement === 'left' && <FormOptionUi />}
    </label>
  );
};

FormCheckboxElement.defaultProps = {
  name: T.string,
  textPlacement: T.string,
  className: T.string,
  title: T.string,
  checked: T.bool,
  hideText: T.bool,
  children: T.node,
  onChange: T.func
};

/**
 * Form option extend. Common code to all form options.
 */
const formOption = css`
  display: inline-flex;
  font-size: 1rem;
  line-height: 1.5;
  cursor: pointer;

  input {
    flex: none;
  }
`;

const FormOptionText = styled.span`
  line-height: 1.5;
`;

const FormOptionUi = styled.span`
  position: relative;
  transition: all 0.16s ease 0s;
`;

export const FormCheckbox = styled(FormCheckboxElement)`
  ${formOption}

  input {
    ${visuallyHidden()};
  }

  ${FormOptionUi} {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0.125rem 0;
    height: 1.25rem;
    width: 1.25rem;
    border-radius: ${themeVal('shape.rounded')};
    border: ${themeVal('layout.border')} solid ${_rgba(themeVal('color.base'), 0.16)};
    background: #fff;
    line-height: 1;

    &::before {
      ${collecticon('tick--small')};
      transition: all 0.24s ease 0s;
      opacity: 0;
    }
  }

  &:hover ${/* sc-selector */FormOptionUi}::before {

  }

  ${({ checked }) => (checked ? `${FormOptionUi},` : '')}
  input:checked ~ ${FormOptionUi} { /* stylelint-disable-line */
    &::before {
      opacity: 1;
    }
  }
`;
