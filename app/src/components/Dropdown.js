import React from 'react';
import { PropTypes as T } from 'prop-types';
import TetherComponent from 'react-tether';
import { CSSTransition } from 'react-transition-group';
import styled, { css } from 'styled-components';
import { rgba, tint } from 'polished';

import { themeVal, stylizeFunction } from '../styles/utils/general';
import { divide, multiply } from '../styles/utils/math';
import collecticon from '../styles/collecticons';

const _rgba = stylizeFunction(rgba);
const _tint = stylizeFunction(tint);

export const DropdownTrigger = styled.a`
  color: #FFF;
  font-weight: bold;
  &::after {
    margin-left: ${divide(themeVal('layout.space'), 2)};
    ${collecticon('chevron-down--small')};
  }
`;

export const DropdownList = styled.ul`
  margin-left: -${themeVal('layout.space')};
  margin-right: -${themeVal('layout.space')};
`;

export const DropdownItem = styled.li`
  display: flex;
  align-items: center;
  background-color: ${themeVal('color.background')};
  cursor: pointer;
  padding: ${divide(themeVal('layout.space'), 4)} ${themeVal('layout.space')};
  transition: background-color .16s ease;

  &:hover {
    background-color: ${themeVal('color.shadow')};
  }
`;

// Not reassigned but contents are modified.
let activeDropdowns = []; // eslint-disable-line

/*
<Dropdown
  className='browse-menu'
  triggerElement={<button>Hello</button>}
  direction='down'
  alignment='center' >

  <h6 className='drop__title'>Browse</h6>
  <ul className='drop__menu drop__menu--select'>
    <li><Link to='' className='drop__menu-item' activeClassName='drop__menu-item--active'>Label</Link></li>
  </ul>

</Dropdown>
*/
export default class Dropdown extends React.Component {
  static closeAll() {
    activeDropdowns.forEach(d => d.close());
  }

  constructor(props) {
    super(props);

    this.uuid = Math.random().toString(36).substr(2, 5);

    this.state = {
      open: false
    };

    this._bodyListener = this._bodyListener.bind(this);
    this._toggleDropdown = this._toggleDropdown.bind(this);
  }

  // Lifecycle method.
  // Called once as soon as the component has a DOM representation.
  componentDidMount() {
    activeDropdowns.push(this);
    window.addEventListener('click', this._bodyListener); // eslint-disable-line
  }

  // Lifecycle method.
  componentWillUnmount() {
    activeDropdowns.splice(activeDropdowns.indexOf(this), 1);
    window.removeEventListener('click', this._bodyListener); // eslint-disable-line
  }

  _bodyListener(e) {
    const attrHook = el => el.getAttribute ? el.getAttribute('data-hook') : null;
    // Get the dropdown that is a parent of the clicked element. If any.
    const theSelf = e.target;
    if (theSelf.tagName === 'BODY'
      || theSelf.tagName === 'HTML'
      || attrHook(theSelf) === 'dropdown:close') {
      this.close();
      return;
    }

    const getClosestInstance = (el) => {
      do {
        // If the click is released outside the view port, the el will be
        // HTMLDocument and won't have hasAttribute method.
        if (el && el.hasAttribute && el.hasAttribute('data-drop-instance')) {
          return el;
        }
        el = el.parentNode;  // eslint-disable-line
      } while (el && el.tagName !== 'BODY' && el.tagName !== 'HTML');

      return null;
    };

    // The closest instance is the closest parent element with a
    // data-drop-instance. It also has a data-drop-el which can be trigger
    // or content. Depending on this we know if we're handling a trigger click
    // or a click somewhere else.
    const closestInstance = getClosestInstance(theSelf);
    if (!closestInstance) return this.close();

    const uuid = closestInstance.getAttribute('data-drop-instance');
    if (closestInstance.getAttribute('data-drop-el') === 'trigger' && uuid === this.uuid) {
      // If we're dealing with the trigger for this instance don't do anything.
      // There are other listeners in place.
      return;
    }

    if (closestInstance.getAttribute('data-drop-el') === 'content' && uuid === this.uuid) {
      // If we're dealing with the content for this instance don't do anything.
      // The content elements can use data-hook='dropdown:close' if they need to
      // close the dropdown, otherwise a trigger click is needed.
      return;
    }

    // In all other cases close the dropdown.
    this.close();
  }

  _toggleDropdown(e) {
    e.preventDefault();
    this.toggle();
  }

  toggle() {
    this.setState(state => ({ open: !state.open }));
  }

  open() {
    !this.state.open && this.setState({ open: true });  // eslint-disable-line
  }

  close() {
    this.state.open && this.setState({ open: false });  // eslint-disable-line
  }

  renderTriggerElement() {
    const {
      triggerElement
    } = this.props;

    const { open } = this.state;

    const className = triggerElement.props.className || '';
    return React.cloneElement(triggerElement, {
      onClick: this._toggleDropdown,
      active: open,
      className: className + (open ? ' active' : ''),
      'data-drop-el': 'trigger',
      'data-drop-instance': this.uuid
    });
  }

  renderContent() {
    const { id, direction, className } = this.props;

    // Base and additional classes for the trigger and the content.
    let klasses = ['drop__content', 'drop-trans', `drop-trans--${direction}`]; // eslint-disable-line
    let dropdownContentProps = { // eslint-disable-line
      'data-drop-instance': this.uuid,
      'data-drop-el': 'content'
    };

    if (className) {
      klasses.push(className);
    }

    dropdownContentProps.direction = direction;
    dropdownContentProps.className = klasses.join(' ');

    if (id) {
      dropdownContentProps.id = id;
    }

    const { open } = this.state;
    const { onChange, children } = this.props;

    return (
      <CSSTransition
        in={open}
        appear
        unmountOnExit
        classNames="drop-trans"
        timeout={{ enter: 300, exit: 300 }}
      >

        <TransitionItem
          props={dropdownContentProps}
          onChange={onChange}
        >
          { children }
        </TransitionItem>

      </CSSTransition>
    );
  }

  render() {
    const { alignment, direction } = this.props;

    let allowed;
    if (direction === 'up' || direction === 'down') {
      allowed = ['left', 'center', 'right'];
    } else if (direction === 'left' || direction === 'right') {
      allowed = ['top', 'middle', 'bottom'];
    } else {
      throw new Error(`Dropdown: direction "${direction}" is not supported. Use one of: up, down, left, right`);
    }

    if (allowed.indexOf(alignment) === -1) {
      throw new Error(`Dropdown: alignment "${alignment}" is not supported when direction is ${direction}. Use one of: ${allowed.join(', ')}`);
    }

    let tetherAttachment;
    let tetherTargetAttachment;
    switch (direction) {
      case 'up':
        tetherAttachment = `bottom ${alignment}`;
        tetherTargetAttachment = `top ${alignment}`;
        break;
      case 'down':
        tetherAttachment = `top ${alignment}`;
        tetherTargetAttachment = `bottom ${alignment}`;
        break;
      case 'right':
        tetherAttachment = `${alignment} left`;
        tetherTargetAttachment = `${alignment} right`;
        break;
      case 'left':
        tetherAttachment = `${alignment} right`;
        tetherTargetAttachment = `${alignment} left`;
        break;
    }

    // attachment={tetherAttachment}
    // targetAttachment={tetherTargetAttachment}
    return (
      <TetherComponent
        // attachment is the content.
        attachment={tetherAttachment}
        // targetAttachment is the trigger
        targetAttachment={tetherTargetAttachment}
        constraints={[{
          to: 'window',
          attachment: 'together'
        }]}
      >
        {this.renderTriggerElement()}
        {this.renderContent()}
      </TetherComponent>
    );
  }
}

Dropdown.defaultProps = {
  triggerElement: 'button',
  direction: 'down',
  alignment: 'center'
};

if (process.env.NODE_ENV !== 'production') {
  Dropdown.propTypes = {
    id: T.string,
    onChange: T.func,

    triggerElement: T.node,

    direction: T.oneOf(['up', 'down', 'left', 'right']),
    alignment: T.oneOf(['left', 'center', 'right', 'top', 'middle', 'bottom']),

    className: T.string,
    children: T.node
  };
}

const transitions = {
  up: {
    start: () => css`
      opacity: 0;
      transform: translate(0, ${themeVal('layout.space')});
    `,
    end: () => css`
      opacity: 1;
      transform: translate(0, -${themeVal('layout.space')});
    `
  },
  down: {
    start: () => css`
      opacity: 0;
      transform: translate(0, -${themeVal('layout.space')});
    `,
    end: () => css`
      opacity: 1;
      transform: translate(0, ${themeVal('layout.space')});
    `
  },
  left: {
    start: () => css`
      opacity: 0;
      transform: translate(${themeVal('layout.space')}, 0);
    `,
    end: () => css`
      opacity: 1;
      transform: translate(-${themeVal('layout.space')}, 0);
    `
  },
  right: {
    start: () => css`
      opacity: 0;
      transform: translate(-${themeVal('layout.space')}, 0);
    `,
    end: () => css`
      opacity: 1;
      transform: translate(${themeVal('layout.space')}, 0);
    `
  }
};

const DropContent = styled.div`
  background: #fff;
  border-radius: ${themeVal('shape.rounded')};
  box-shadow: 0 0 32px 2px ${_rgba(themeVal('color.base'), 0.08)}, 0 16px 48px -16px ${_rgba(themeVal('color.base'), 0.16)};
  position: relative;
  z-index: 1000;
  width: 100%;
  max-width: 14rem;
  margin: 0;
  padding: ${themeVal('layout.space')};
  overflow: hidden;
  text-align: left;
  color: ${themeVal('type.base.color')};
  font-size: 1rem;
  line-height: 1.5;
  transition: opacity 0.16s ease, transform 0.16s ease;

  .tether-target-attached-top.tether-element-attached-bottom & {
    ${transitions.up.end}

    &.drop-trans-exit {
      ${transitions.up.end}
    }

    &.drop-trans-exit-active {
      ${transitions.up.start}
    }
  }

  .tether-target-attached-bottom.tether-element-attached-top & {
    ${transitions.down.end}

    &.drop-trans-exit {
      ${transitions.down.end}
    }

    &.drop-trans-exit-active {
      ${transitions.down.start}
    }
  }

  .tether-target-attached-right.tether-element-attached-left & {
    ${transitions.right.end}

    &.drop-trans-exit {
      ${transitions.right.end}
    }

    &.drop-trans-exit-active {
      ${transitions.right.start}
    }
  }

  .tether-target-attached-left.tether-element-attached-right & {
    ${transitions.left.end}

    &.drop-trans-exit {
      ${transitions.left.end}
    }

    &.drop-trans-exit-active {
      ${transitions.left.start}
    }
  }

  /* ${({ direction }) => transitions[direction].end}

  &.drop-trans-appear,
  &.drop-trans-enter {
    ${({ direction }) => transitions[direction].start}
  }

  &&.drop-trans-enter-active,
  &&.drop-trans-appear-active {
    ${({ direction }) => transitions[direction].end}
  }

  &.drop-trans-exit {
    ${({ direction }) => transitions[direction].end}
  }

  &&.drop-trans-exit-active {
    ${({ direction }) => transitions[direction].start}
  } */
`;

class TransitionItem extends React.Component {
  componentDidMount() {
    const { onChange } = this.props;
    onChange && onChange(true); // eslint-disable-line
  }

  componentWillUnmount() {
    const { onChange } = this.props;
    onChange && onChange(false); // eslint-disable-line
  }

  render() {
    const { props, children } = this.props;
    return <DropContent {...props}>{ children }</DropContent>;
  }
}

if (process.env.NODE_ENV !== 'production') {
  TransitionItem.propTypes = {
    onChange: T.func,
    props: T.object,
    children: T.node
  };
}

const glbS = themeVal('layout.space');

// Drop content elements.
export const DropMenu = styled.ul`
  list-style: none;
  margin: -${glbS} -${glbS} ${glbS} -${glbS};
  box-shadow: 0 ${themeVal('layout.border')} 0 0 ${themeVal('color.shadow')};
  padding: ${divide(glbS, 2)} 0;
  min-width: 12rem;

  /* Styles when the ul items have icons */
  ${({ iconified }) => iconified && css`
    ${DropMenuItem} {
      padding-left: ${multiply(glbS, 2.75)};

      &::before {
        position: absolute;
        z-index: 1;
        top: ${divide(glbS, 4)};
        left: ${glbS};
        font-size: 1rem;
        line-height: 1.5rem;
        width: 1.5rem;
        text-align: center;
      }
    }
  `}

  &:last-child {
    margin-bottom: -${glbS};
    box-shadow: none;
  }
`;

export const DropMenuItem = styled.span`
  position: relative;
  display: block;
  padding: 0.25rem 1rem;
  color: ${themeVal('type.base.color')};
  transition: all 0.16s ease 0s;

  &:hover,
  &:focus {
    background-color: ${_rgba(themeVal('color.base'), 0.04)};
    opacity: 1;
  }

  &:visited {
    color: inherit;
  }

  ${({ active }) => active && css`
    color: inherit;

    &::after {
      ${collecticon('tick--small')}
      position: absolute;
      z-index: 1;
      top: ${divide(themeVal('layout.space'), 4)};
      right: ${divide(themeVal('layout.space'), 2)};
      font-size: 1rem;
      line-height: 1.5rem;
      opacity: 0.48;
      width: 1.5rem;
      text-align: center;
    }
  `}
`;

export const DropInset = styled.div`
  background: ${_tint(0.96, themeVal('color.base'))};
  color: ${_tint(0.32, themeVal('type.base.color'))};
  box-shadow:
    inset 0 ${themeVal('layout.border')} 0 0 ${themeVal('color.shadow')},
    inset 0 -${themeVal('layout.border')} 0 0 ${themeVal('color.shadow')};
  margin: -${glbS} -${glbS} ${glbS} -${glbS};
  padding: ${glbS};

  &:first-child {
    box-shadow: inset 0 -${themeVal('layout.border')} 0 0 ${themeVal('color.shadow')};
  }

  &:last-child {
    margin-bottom: -${glbS};
    box-shadow: inset 0 ${themeVal('layout.border')} 0 0 ${themeVal('color.shadow')};
  }

  &:only-child {
    box-shadow: none;
  }

  > *:first-child {
    margin-top: 0;
  }

  > *:last-child {
    margin-bottom: 0;
  }
`;
