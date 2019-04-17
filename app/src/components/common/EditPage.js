import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { push } from 'connected-react-router';
import { connect } from 'react-redux';
import styled from 'styled-components';
import { rgba } from 'polished';
import { themeVal, stylizeFunction } from '../../styles/utils/general';
import { multiply } from '../../styles/utils/math';
import { headingAlt } from '../../styles/atoms/type/heading';
import collecticon from '../../styles/collecticons';

import {
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageTagline,
  InpageToolbar,
  InpageBody,
  InpageBodyInner
} from './Inpage';

import {
  atbdsedit,
  introduction,
  contacts,
  drafts,
  algorithm_description,
  algorithm_usage
} from '../../constants/routes';

import Dropdown, {
  DropdownTrigger,
  DropdownList,
  DropdownItem
} from '../Dropdown';

const _rgba = stylizeFunction(rgba);

const Stepper = styled.div`
  display: flex;
  flex-flow: row nowrap;
  line-height: 2rem;

  > * {
    display: inline-flex;
  }
`;

const StepperLabel = styled.div`
  ${headingAlt()}
  font-size: 0.875rem;
  margin: 0;
  color: ${_rgba('#FFFFFF', 0.64)};
  margin-right: 0.5rem;
`;

export const EditorSection = styled.div`
  background-color: ${themeVal('color.lightgray')};
  padding: ${multiply(themeVal('layout.space'), 2)};
  margin-top: ${multiply(themeVal('layout.space'), 2)};
  margin-bottom: ${multiply(themeVal('layout.space'), 2)};
`;

export const EditorSectionTitle = styled.h4`
  font-size: 1em;
  font-weight: bold;
  line-height: 2;
  margin: 0;
`;

export const EditorLabel = styled.label`
  color: ${themeVal('color.darkgray')};
  display: block;
  font-size: 0.875rem;
  font-weight: lighter;
  line-height: 2;
  margin-bottom: ${multiply(themeVal('layout.space'), 2)};
  margin-top: ${multiply(themeVal('layout.space'), 2)};
  text-transform: uppercase;
  &&:first-child {
    margin-top: 0;
  }
`;

export const RemovableListItem = styled.li`
  &::before {
    cursor: pointer;
    ${collecticon('xmark--small')}
  }
`;

const Item = styled(DropdownItem)`
  border-top: 1px solid ${themeVal('color.lightgray')};
  font-weight: bold;
  padding: ${multiply(themeVal('layout.space'), 0.5)} ${themeVal('layout.space')};
  text-align: left;
`;

const ItemCount = styled.span`
  align-items: center;
  color: #FFF;
  background-color: ${themeVal('color.darkgray')};
  border-radius: ${multiply(themeVal('layout.space'), 1.2)};
  display: inline-flex;
  justify-content: center;
  height: ${multiply(themeVal('layout.space'), 2)};
  margin-right: ${multiply(themeVal('layout.space'), 0.5)};
  width: ${multiply(themeVal('layout.space'), 2)};
`;

const EditPage = (props) => {
  const {
    title,
    step,
    id,
    children
  } = props;

  const version = 1;

  const items = [
    { display: 'Identifying information' },
    { display: 'Introduction', link: `/${atbdsedit}/${id}/${drafts}/${version}/${introduction}` },
    { display: 'Contact information', link: `/${atbdsedit}/${id}/${contacts}` },
    { display: 'Algorithm description', link: `/${atbdsedit}/${id}/${drafts}/${version}/${algorithm_description}` },
    { display: 'Algorithm usage', link: `/${atbdsedit}/${id}/${drafts}/${version}/${algorithm_usage}` },
    { display: 'Algorithm implementation' },
    { display: 'References' }
  ];

  const numSteps = items.length;
  const stepCount = `Step ${step} of ${numSteps}`;

  return (
    <Fragment>
      <InpageHeader>
        <InpageHeaderInner>
          <InpageHeadline>
            <InpageTitle>{ title }</InpageTitle>
            <InpageTagline>Editing document</InpageTagline>
          </InpageHeadline>
          <InpageToolbar>
            <Stepper>
              <StepperLabel>
                { stepCount }
              </StepperLabel>
              <Dropdown
                triggerText={items[step - 1].display}
                triggerTitle="Toggle menu options"
                triggerElement={DropdownTrigger}
              >
                <DropdownList>
                  {items.map((d, i) => (
                    <Item
                      key={d.display}
                      onClick={() => d.link && props.push(d.link)}
                    >
                      <ItemCount>{i + 1}</ItemCount>
                      {d.display}
                    </Item>
                  ))}
                </DropdownList>
              </Dropdown>
            </Stepper>
            <a href="#" title="Save document">Save</a>
            <a href="#" title="Cancel edit">Cancel</a>
          </InpageToolbar>
        </InpageHeaderInner>
      </InpageHeader>
      <InpageBody>
        <InpageBodyInner>
          { children }
        </InpageBodyInner>
      </InpageBody>
    </Fragment>
  );
};

EditPage.propTypes = {
  title: PropTypes.string.isRequired,
  step: PropTypes.number,
  id: PropTypes.number,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ]),
  push: PropTypes.func,
};

const mapStateToProps = () => ({});
const mapDispatch = { push };

export default connect(mapStateToProps, mapDispatch)(EditPage);
