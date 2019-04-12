import React, { Component } from 'react';
import styled from 'styled-components';
import ReactTooltip from 'react-tooltip';

import { themeVal } from '../../styles/utils/general';
import collecticon from '../../styles/collecticons';

import {
  Inpage,
  InpageHeader,
  InpageHeaderInner,
  InpageHeadline,
  InpageTitle,
  InpageBody,
  InpageBodyInner
} from '../common/Inpage';
import Prose from '../../styles/type/prose';
import Button from '../../styles/button/button';
import Form from '../../styles/form/form';
import {
  FormFieldset,
  FormFieldsetHeader
} from '../../styles/form/fieldset';
import FormLegend from '../../styles/form/legend';
import {
  FormGroup,
  FormGroupHeader,
  FormGroupBody
} from '../../styles/form/group';
import FormLabel from '../../styles/form/label';
import FormInput from '../../styles/form/input';
import FormToolbar from '../../styles/form/toolbar';
import ButtonGroup from '../../styles/button/group';
import {
  FormHelper,
  FormHelperMessage,
  FormHelperCounter
} from '../../styles/form/helper';

// Create a ul component to include some styling.

const Ul = styled.ul`
  > li {
    margin-bottom: 1rem;
  }

  > li:last-child {
    margin-bottom: 0;
  }
`;

// Extend the component previously created to change the background
// This is needed to see the achromic buttons.

const DarkUl = styled(Ul)`
  background: ${themeVal('color.base')};
`;

// Extend a button to add an icon.

const ButtonIconBrand = styled(Button)`
  ::before {
    ${collecticon('plus')}
  }
`;

const RemoveButton = styled(Button)`
  ::before {
    ${collecticon('trash-bin')}
  }
`;

const InfoButton = styled(Button)`
  ::before {
    ${collecticon('circle-information')}
  }
`;

// Below the differente button variations and sizes to render all buttons.

const variations = [
  'base-raised-light',
  'base-raised-semidark',
  'base-raised-dark',
  'base-plain',
  'primary-raised-light',
  'primary-raised-semidark',
  'primary-raised-dark',
  'primary-plain',
  'danger-raised-light',
  'danger-raised-dark',
  'danger-plain'
];

const lightVariations = ['achromic-plain', 'achromic-glass'];

const sizes = ['small', 'default', 'large', 'xlarge'];

class Sandbox extends Component {
  render() {
    return (
      <Inpage>
        <InpageHeader>
          <InpageHeaderInner>
            <InpageHeadline>
              <InpageTitle>Sandbox</InpageTitle>
            </InpageHeadline>
          </InpageHeaderInner>
        </InpageHeader>
        <InpageBody>
          <InpageBodyInner>
            <Prose>
              <h2>Form elements</h2>
              <Form>
                <FormFieldset>
                  <FormFieldsetHeader>
                    <FormLegend>Form legend</FormLegend>
                    <RemoveButton
                      variation="base-plain"
                      size="small"
                      hideText
                    >
                      Remove fieldset
                    </RemoveButton>
                  </FormFieldsetHeader>
                  <FormGroup>
                    <FormGroupHeader>
                      <FormLabel htmlFor="input-text-a" optional>Form label</FormLabel>
                      <FormToolbar>
                        <InfoButton
                          variation="base-plain"
                          size="small"
                          hideText
                          data-tip="This is a very helpful tooltip."
                        >
                          Learn more
                        </InfoButton>
                        <ReactTooltip effect="solid" className="type-primary" />
                      </FormToolbar>
                    </FormGroupHeader>
                    <FormGroupBody>
                      <FormInput
                        type="text"
                        size="large"
                        id="input-text-a"

                        placeholder="This is a text input"
                      />
                      <FormHelper>
                        <FormHelperMessage>This is some help text.</FormHelperMessage>
                        <FormHelperCounter>0 / 80</FormHelperCounter>
                      </FormHelper>
                    </FormGroupBody>
                  </FormGroup>
                </FormFieldset>
              </Form>

              <h2>Button Group</h2>
              <ButtonGroup orientation="horizontal">
                <Button variation="base-raised-light">First</Button>
                <Button variation="base-raised-light">Second</Button>
                <Button variation="base-raised-light">Third</Button>
                <Button variation="base-raised-light">Last</Button>
              </ButtonGroup>
              <ButtonGroup orientation="horizontal">
                <ButtonIconBrand variation="base-raised-light">
                  First
                </ButtonIconBrand>
                <ButtonIconBrand variation="base-raised-light">
                  Second
                </ButtonIconBrand>
                <ButtonIconBrand variation="base-raised-light">
                  Third
                </ButtonIconBrand>
              </ButtonGroup>
              <ButtonGroup orientation="vertical">
                <Button variation="base-raised-light">First</Button>
                <Button variation="base-raised-light">Second</Button>
                <Button variation="base-raised-light">Third</Button>
                <Button variation="base-raised-light">Last</Button>
              </ButtonGroup>

              <h2>Buttons</h2>
              <ButtonIconBrand variation="base-raised-light">
                I have an icon
              </ButtonIconBrand>
              <ButtonIconBrand variation="base-raised-light" hideText>
                this text is hidden
              </ButtonIconBrand>

              {variations.map(variation => (
                <Ul key={variation}>
                  {sizes.map(size => (
                    <li key={size}>
                      <Button variation={variation} size={size}>
                        {size} - {variation}
                      </Button>
                    </li>
                  ))}
                </Ul>
              ))}
              {lightVariations.map(variation => (
                <DarkUl key={variation}>
                  {sizes.map(size => (
                    <li key={size}>
                      <Button variation={variation} size={size}>
                        {size} - {variation}
                      </Button>
                    </li>
                  ))}
                </DarkUl>
              ))}
            </Prose>
          </InpageBodyInner>
        </InpageBody>
      </Inpage>
    );
  }
}

export default Sandbox;
