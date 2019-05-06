import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Button from '../styles/button/button';
import { serializeDocument } from '../actions/actions';

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

  const pdfReady = atbd_id === serializing_id && pdf;
  let pdfLabel = 'Create Pdf';
  if (pdfReady) {
    pdfLabel = <a href={pdf}>View Pdf</a>;
  }
  if (atbd_id === serializing_id && !pdf) {
    pdfLabel = 'Creating';
  }
  return (
    <Button
      variation="base-raised-light"
      onClick={() => {
        serialize({
          atbd_id,
          atbd_version
        });
      }}
    >
      {pdfLabel}
    </Button>
  );
};

const mapDispatchToProps = { serializeDocument };

const mapStateToProps = (state) => {
  const { serializingAtbdVersion } = state.application;
  return { serializingAtbdVersion };
};
export default connect(mapStateToProps, mapDispatchToProps)(AtbdPreview);
