import React from 'react';
import ReactTooltip from 'react-tooltip';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';

import Button from '../../styles/button/button';
import collecticon from '../../styles/collecticons';

const Btn = styled(Button)`
  ::before {
    ${collecticon('circle-information')}
  }
`;

export default function InfoButton({ text }) {
  if (!text) return null;
  return (
    <React.Fragment>
      <Btn
        variation="base-plain"
        size="small"
        hideText
        data-tip={text}
      >
        Learn more
      </Btn>
      <ReactTooltip effect="solid" className="type-primary" />
    </React.Fragment>
  );
}

InfoButton.propTypes = {
  text: PropTypes.string
};
