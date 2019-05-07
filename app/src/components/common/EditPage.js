import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { push } from 'connected-react-router';
import { connect } from 'react-redux';
import { StickyContainer, Sticky } from 'react-sticky';
import styled from 'styled-components/macro';
import { rgba } from 'polished';
import { themeVal, stylizeFunction } from '../../styles/utils/general';
import { antialiased } from '../../styles/helpers';
import { headingAlt } from '../../styles/type/heading';
import Button from '../../styles/button/button';
import { VerticalDivider } from '../../styles/divider';
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
  identifying_information,
  introduction,
  contacts,
  drafts,
  algorithm_description,
  algorithm_usage,
  algorithm_implementation,
  references
} from '../../constants/routes';

import Prose from '../../styles/type/prose';

import Dropdown, {
  DropTitle,
  DropMenu,
  DropMenuItem
} from '../Dropdown';

const _rgba = stylizeFunction(rgba);


const StepperDrop = styled(Dropdown)`
  min-width: 20rem;
`;

const PrevButton = styled(Button)`
  &::before {
    ${collecticon('chevron-left--small')}
  }
`;

const NextButton = styled(Button)`
  &::after {
    ${collecticon('chevron-right--small')}
  }
`;

const StepDropTrigger = styled(Button)`
  &::after {
    ${collecticon('chevron-down--small')}
  }
`;

const Stepper = styled.div`
  display: flex;
  flex-flow: row nowrap;
  line-height: 2rem;

  > * {
    display: inline-flex;
  }
`;

const StepperLabel = styled.h6`
  ${headingAlt()}
  font-size: 0.875rem;
  color: ${_rgba('#FFFFFF', 0.64)};
  margin-right: 0.5rem;
`;

export const RemovableListItem = styled.li`
  &::before {
    cursor: pointer;
    ${collecticon('xmark--small')}
  }
`;

const ItemCount = styled.span`
  ${antialiased}
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  line-height: 1.5rem;
  color: #FFF;
  background-color: ${themeVal('color.link')};
  border-radius: ${themeVal('shape.ellipsoid')};
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;

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
    { display: 'Identifying information', link: `/${atbdsedit}/${id}/${drafts}/${version}/${identifying_information}` },
    { display: 'Introduction', link: `/${atbdsedit}/${id}/${drafts}/${version}/${introduction}` },
    { display: 'Contact information', link: `/${atbdsedit}/${id}/${drafts}/${version}/${contacts}` },
    { display: 'Algorithm description', link: `/${atbdsedit}/${id}/${drafts}/${version}/${algorithm_description}` },
    { display: 'Algorithm usage', link: `/${atbdsedit}/${id}/${drafts}/${version}/${algorithm_usage}` },
    { display: 'Algorithm implementation', link: `/${atbdsedit}/${id}/${drafts}/${version}/${algorithm_implementation}` },
    { display: 'References', link: `/${atbdsedit}/${id}/${drafts}/${version}/${references}` }
  ];

  const numSteps = items.length;
  const stepCount = `Step ${step} of ${numSteps}`;

  return (
    <Fragment>
      <StickyContainer>
        <Sticky>
          {stickyProps => (
            <InpageHeader style={stickyProps.style} isSticky={stickyProps.isSticky}>
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
                    <StepperDrop
                      alignment="right"
                      triggerElement={
                        <StepDropTrigger variation="achromic-plain" title="Toggle menu options">{items[step - 1].display}</StepDropTrigger>
                      }
                    >
                      <DropTitle>Select step</DropTitle>
                      <DropMenu role="menu" selectable>
                        {items.map((d, i) => (
                          <li>
                            <DropMenuItem
                              key={d.display}
                              onClick={() => d.link && props.push(d.link)}
                              active={i === step - 1}
                            >
                              <ItemCount>{i + 1}</ItemCount>
                              <span>{d.display}</span>
                            </DropMenuItem>
                          </li>
                        ))}
                      </DropMenu>
                    </StepperDrop>
                  </Stepper>
                  <VerticalDivider />
                  <PrevButton
                    variation="achromic-plain"
                    title="View previous step"
                    onClick={() => items[step - 2].link && props.push(items[step - 2].link)}
                    disabled={(step === 1)}
                  > Prev
                  </PrevButton>
                  <NextButton
                    variation="achromic-plain"
                    title="View next step"
                    onClick={() => items[step].link && props.push(items[step].link)}
                    disabled={(step === 7)}
                  > Next
                  </NextButton>
                </InpageToolbar>
              </InpageHeaderInner>
            </InpageHeader>
          )}
        </Sticky>
        <InpageBody>
          <InpageBodyInner>
            <Prose>
              { children }
            </Prose>
          </InpageBodyInner>
        </InpageBody>
      </StickyContainer>
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
