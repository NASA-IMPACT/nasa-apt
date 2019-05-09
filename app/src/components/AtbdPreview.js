import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import styled from 'styled-components';
import Button from '../styles/button/button';
import collecticon from '../styles/collecticons';
import { serializeDocument } from '../actions/actions';

const Link = styled.a`
  margin-left: 1rem
`;

const DocTablePreviewButton = styled(Button)`
  &::before {
    ${collecticon('eye')};
  }
`;

const AtbdPreview = (props) => {
  const {
    atbd_id,
    atbd_version,
    serializingAtbdVersion,
    serializeDocument: serialize
  } = props;

  const {
    atbd_id: serializing_id,
    pdf,
    html
  } = serializingAtbdVersion || {};

  let label = 'Preview';
  let pdfLink = <span />;
  let htmlLink = <span />;
  if (atbd_id === serializing_id && pdf) {
    pdfLink = <Link target="_blank" href={pdf}>PDF</Link>;
  }
  if (atbd_id === serializing_id && html) {
    htmlLink = <Link target="_blank" href={html}>HTML</Link>;
  }
  if (atbd_id === serializing_id && !(pdf && html)) {
    label = 'Creating';
  }
  return (
    <Fragment>
      {pdfLink}
      {htmlLink}
      <DocTablePreviewButton
        variation="primary-plain"
        size="small"
        title="Preview document"
        onClick={() => {
          serialize({
            atbd_id,
            atbd_version
          });
        }}
      >
        {label}
      </DocTablePreviewButton>
    </Fragment>
  );
};

AtbdPreview.propTypes = {
  atbd_id: PropTypes.number.isRequired,
  atbd_version: PropTypes.number.isRequired,
  serializeDocument: PropTypes.func.isRequired,
  serializingAtbdVersion: PropTypes.object
};

const mapDispatchToProps = { serializeDocument };

const mapStateToProps = (state) => {
  const { serializingAtbdVersion } = state.application;
  return { serializingAtbdVersion };
};
export default connect(mapStateToProps, mapDispatchToProps)(AtbdPreview);
