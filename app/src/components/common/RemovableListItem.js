import React from 'react';
import PropTypes from 'prop-types';

import styled from 'styled-components/macro';
import { multiply } from '../../styles/utils/math';
import collecticon from '../../styles/collecticons';
import { themeVal } from '../../styles/utils/general';

const DeleteIcon = styled('span')`
  cursor: pointer ;
  &:hover {
    color: ${themeVal('color.danger')}
  }
  &::before {
    margin-left: ${multiply(themeVal('layout.space'), 0.5)};
    vertical-align: middle;
    ${collecticon('trash-bin')}
  }
`;

const Label = styled('span')`
  vertical-align: middle
`;

const RemovableListItem = (props) => {
  const {
    label,
    deleteAction
  } = props;
  return (
    <li>
      <Label>
        {label}
      </Label>
      <DeleteIcon onClick={deleteAction} />
    </li>
  );
};

RemovableListItem.propTypes = {
  label: PropTypes.string.isRequired,
  deleteAction: PropTypes.func.isRequired
};

export default RemovableListItem;
