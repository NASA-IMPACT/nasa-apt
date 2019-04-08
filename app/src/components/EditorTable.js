import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import { themeVal } from '../styles/utils/general';
import {
  ToolbarAction,
  ToolbarIcon
} from './Toolbars';

const TableContainer = styled.div`
  position: relative;
`;

const TableActionsTopRight = styled.div`
  position: absolute;
  right: 0;
  top: -2.4rem;
`;

const TableActionsTopLeft = styled.div`
  top: -2.4rem;
  position: absolute;
`;

const TableActionsLeft = styled.div`
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  left: -2.4rem;
  position: absolute;
`;

const TableAction = styled(ToolbarAction)`
  color: ${themeVal('color.surface')};
  display: inline-block;
  background: ${themeVal('color.darkgray')};
  padding: 0.5rem;

  &:first-child {
    border-top-left-radius: 0.25rem;
    border-bottom-left-radius: 0.25rem;
  }

  &:last-child {
    border-top-right-radius: 0.25rem;
    border-bottom-right-radius: 0.25rem;
  }

  &:hover {
    color: ${themeVal('color.base')};
  }

  &:active {
     box-shadow: ${themeVal('boxShadow.inset')};
  }
`;

const ColumnTableAction = styled(TableAction)`
  &:first-child {
    border-top-left-radius: 0.25rem;
    border-top-right-radius: 0.25rem;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  &:last-child {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-left-radius: 0.25rem;
    border-bottom-right-radius: 0.25rem;
  }
`;

const TableIcon = styled(ToolbarIcon)`
  &::before {
    margin-right: 0;
  }
`;

/**
 * split child rows into thead contens and body contents,
 * unless "headless" option is set
 */
function splitHeader({ children, node }) {
  const header = !node.get('data').get('headless');
  if (!header || !children || !children.length || children.length === 1) {
    return { header: null, rows: children };
  }
  return {
    header: children[0],
    rows: children.slice(1)
  };
}

export function EditorTable(props) {
  const {
    attributes,
    isFocused,
    remove,
    insertColumn,
    removeColumn,
    insertRow,
    removeRow
  } = props;
  const { header, rows } = splitHeader(props);
  return (
    <TableContainer>
      {!!isFocused && (
        <div contentEditable={false}>
          <TableActionsTopRight>
            <TableAction onClick={remove}>
              <TableIcon icon={{ icon: 'trash-bin' }} />
            </TableAction>
          </TableActionsTopRight>

          <TableActionsTopLeft>
            <TableAction onClick={removeColumn}>
              <TableIcon icon={{ icon: 'minus' }} />
            </TableAction>
            <TableAction onClick={insertColumn}>
              <TableIcon icon={{ icon: 'plus' }} />
            </TableAction>
          </TableActionsTopLeft>

          <TableActionsLeft>
            <ColumnTableAction onClick={removeRow}>
              <TableIcon icon={{ icon: 'minus' }} />
            </ColumnTableAction>
            <ColumnTableAction onClick={insertRow}>
              <TableIcon icon={{ icon: 'plus' }} />
            </ColumnTableAction>
          </TableActionsLeft>
        </div>
      )}
      <table>
        {!!header && <thead {...attributes}>{header}</thead>}
        <tbody {...attributes}>{rows}</tbody>
      </table>
    </TableContainer>
  );
}

EditorTable.propTypes = {
  attributes: PropTypes.object.isRequired,
  isFocused: PropTypes.bool,
  remove: PropTypes.func.isRequired,
  insertColumn: PropTypes.func.isRequired,
  removeColumn: PropTypes.func.isRequired,
  insertRow: PropTypes.func.isRequired,
  removeRow: PropTypes.func.isRequired
};

export default EditorTable;
