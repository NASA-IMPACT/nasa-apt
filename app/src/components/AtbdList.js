import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import styled from 'styled-components';
import { themeVal } from '../styles/utils/general';
import { multiply } from '../styles/utils/math';
import PageSubNav, {
  SubNavTitle,
  SubNavFilter,
  SubNavActions,
  SubNavAction
} from './common/PageSubNav';

const Separator = styled.span`
  border-right: 1px solid ${themeVal('color.shadow')};
  padding-right: ${multiply(themeVal('layout.space'), 2)};
  margin-right: ${multiply(themeVal('layout.space'), 2)};
`

const AtbdList = (props) => {
  const { atbds } = props;
  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title } = atbd;
    return <div key={atbd_id}>{title}</div>;
  });
  return (
    <Fragment>
      <PageSubNav>
        <Separator><SubNavTitle>Documents</SubNavTitle></Separator>
        <SubNavFilter></SubNavFilter>

        <SubNavActions>
          <SubNavAction>Search</SubNavAction>
          <SubNavAction>Create</SubNavAction>
        </SubNavActions>
      </PageSubNav>
      {atbdElements}
    </Fragment>
  );
};

AtbdList.propTypes = {
  atbds: PropTypes.arrayOf(PropTypes.shape({
    atbd_id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired
  }))
};

const mapStateToProps = (state) => {
  const { atbds } = state.application;
  return { atbds };
};

export default connect(mapStateToProps)(AtbdList);
