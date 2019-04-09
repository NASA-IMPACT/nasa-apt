import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import Button from '../styles/atoms/button';
import ButtonGroup from '../styles/molecules/button-group';
import collecticon from '../styles/collecticons';

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

const RemoveBtn = styled(Button)`
  ::before {
    ${collecticon('trash-bin')}
  }
`;

const MinusBtn = styled(Button)`
  ::before {
    ${collecticon('minus')}
  }
`;

const PlusBtn = styled(Button)`
  ::before {
    ${collecticon('plus')}
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
            <RemoveBtn
              onClick={remove}
              variation="base-raised-light"
              hideText
            >
              Remove
            </RemoveBtn>
          </TableActionsTopRight>

          <TableActionsTopLeft>
            <ButtonGroup orientation="horizontal">
              <MinusBtn
                onClick={removeColumn}
                variation="base-raised-light"
                hideText
              >
                Remove column
              </MinusBtn>
              <PlusBtn
                onClick={insertColumn}
                variation="base-raised-light"
                hideText
              >
                Add column
              </PlusBtn>
            </ButtonGroup>
          </TableActionsTopLeft>

          <TableActionsLeft>
            <ButtonGroup orientation="vertical">
              <MinusBtn
                onClick={removeRow}
                variation="base-raised-light"
                hideText
              >
                Remove row
              </MinusBtn>
              <PlusBtn
                onClick={insertRow}
                variation="base-raised-light"
                hideText
              >
                Add row
              </PlusBtn>
            </ButtonGroup>
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
