import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

const AtbdList = (props) => {
  const { atbds } = props;
  const atbdElements = atbds.map((atbd) => {
    const { atbd_id, title } = atbd;
    return <div key={atbd_id}>{title}</div>;
  });
  return (
    <Fragment>
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
