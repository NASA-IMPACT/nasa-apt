import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { push } from 'connected-react-router';
import { connect } from 'react-redux';
import Constrainer from '../../styles/atoms/constrainer';
import { atbdsedit } from '../../constants/routes';
import PageSubNav, {
  SubNavTitle,
  SubNavTagline,
  SubNavActions,
  SubNavAction
} from './PageSubNav';
import PageSection from './Page';
import { multiply } from '../../styles/utils/math';
import { themeVal } from '../../styles/utils/general';
import Dropdown, {
  DropdownTrigger,
  DropdownList,
  DropdownItem
} from '../Dropdown';

export const EditorSection = styled.div`
  background-color: ${themeVal('color.lightgray')};
  padding: ${multiply(themeVal('layout.space'), 2)};
  margin-top: ${multiply(themeVal('layout.space'), 2)};
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
  text-transform: uppercase;
`;

export const InputFormGroup = styled.form`
  margin-top: ${themeVal('layout.space')};
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
`;

export const InputLabel = styled.label`
  display: block
  font-weight: bold;
  margin: ${themeVal('layout.space')} 0 0;
  width: 32%;
`;

export const InputLabelFeedback = styled.span`
`;

export const SmallTextInput = styled.input`
  font-family: inherit;
  margin: ${multiply(themeVal('layout.space'), 0.5)} 0 0;
  padding: ${multiply(themeVal('layout.space'), 0.5)};
  width: 100%;
`;

export const InputSubmit = styled.input`
  background: #FFF;
  border: 1px solid ${themeVal('color.lightgray')};
  box-shadow: ${themeVal('boxShadow.input')};
  font-size: 0.875rem;
  font-weight: bold;
  margin: ${themeVal('layout.space')} 0 0;
  padding: ${multiply(themeVal('layout.space'), 0.5)} ${multiply(themeVal('layout.space'), 2)};
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
    numSteps,
    id,
    children
  } = props;

  const items = [
    { display: 'Identifying information' },
    { display: 'Introduction' },
    { display: 'Contact information', link: `/${atbdsedit}/${id}/contacts` },
    { display: 'Algorithm description' },
    { display: 'Algorithm usage' },
    { display: 'Algorithm implementation' },
    { display: 'References' }
  ];

  const stepCount = `Step ${step} of ${numSteps}`;

  return (
    <Fragment>
      <PageSubNav>
        <SubNavTitle>
          <SubNavTagline>Editing Document</SubNavTagline>
          { title }
        </SubNavTitle>

        <SubNavActions>
          <SubNavAction>
            { stepCount }
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
          </SubNavAction>

          <SubNavAction>Cancel</SubNavAction>
          <SubNavAction>Save</SubNavAction>
        </SubNavActions>
      </PageSubNav>
      <PageSection>
        <Constrainer>
          { children }
        </Constrainer>
      </PageSection>
    </Fragment>
  );
};

EditPage.propTypes = {
  title: PropTypes.string.isRequired,
  step: PropTypes.number,
  numSteps: PropTypes.number,
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
