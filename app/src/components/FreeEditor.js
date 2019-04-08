import React from 'react';
import PropTypes from 'prop-types';
import ImmutableTypes from 'react-immutable-proptypes';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import PluginDeepTable from 'slate-deep-table';
import styled from 'styled-components/macro';
import EquationEditor from './EquationEditor';
import TrailingBlock from '../slate-plugins/TrailingBlock';
import {
  ToolbarAction,
  ToolbarIcon,
  Toolbar,
  ToolbarLabel
} from './Toolbars';
import EditorImage from './EditorImage';
import schema from './editorSchema';
import { themeVal } from '../styles/utils/general';
import { multiply } from '../styles/utils/math';

const equation = 'equation';
const paragraph = 'paragraph';
const table = 'table';

const EditorContainer = styled.div`
  background-color: ${themeVal('color.surface')}
  border: 1px solid ${themeVal('color.gray')};
  border-bottom-left-radius: ${multiply(themeVal('layout.space'), 0.25)};
  border-bottom-right-radius: ${multiply(themeVal('layout.space'), 0.25)};
  padding: ${themeVal('layout.space')};
`;

const plugins = [
  TrailingBlock(),
  SoftBreak(),
  PluginDeepTable(),
];

export class FreeEditor extends React.Component {
  constructor(props) {
    super(props);
    const { value } = props;
    this.state = {
      value,
      activeTool: null
    };
    this.onChange = this.onChange.bind(this);
    this.renderNode = this.renderNode.bind(this);
    this.insertEquation = this.insertEquation.bind(this);
    this.insertParagraph = this.insertParagraph.bind(this);
    this.insertTable = this.insertTable.bind(this);
    this.selectTool = this.selectTool.bind(this);
    this.onMouseDown = this.onMouseDown.bind(this);
    this.save = this.save.bind(this);
    this.insertColumn = this.insertColumn.bind(this);
    this.insertRow = this.insertRow.bind(this);
    this.removeColumn = this.removeColumn.bind(this);
    this.removeRow = this.removeRow.bind(this);
    this.removeTable = this.removeTable.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const { value } = nextProps;
    this.setState({ value });
  }

  onMouseDown() {
    const { activeTool } = this.state;
    if (activeTool) {
      setTimeout(() => {
        if (activeTool === equation) {
          this.insertEquation();
        }
        if (activeTool === paragraph) {
          this.insertParagraph();
        }
        if (activeTool === table) {
          this.insertTable();
        }
      }, 0);
    }
  }

  onChange(event) {
    const { value } = event;
    this.setState({
      value,
      activeTool: null
    });
  }

  selectTool(tool) {
    this.setState((state) => {
      if (state.activeTool === tool) {
        return { activeTool: null };
      }
      return { activeTool: tool };
    });
  }

  save(e) {
    e.preventDefault();
    const { save } = this.props;
    const jsonValue = this.editor.value.toJSON();
    save(jsonValue);
  }

  insertEquation() {
    this.editor
      .insertBlock({
        type: equation,
        nodes: [
          {
            object: 'text',
            leaves: [{
              text: '\\',
            }]
          },
        ],
      })
      .focus();
  }

  insertParagraph() {
    this.editor
      .insertBlock({
        type: paragraph,
        nodes: [
          {
            object: 'text',
            leaves: [{
              text: '',
            }]
          },
        ],
      })
      .focus();
  }

  insertTable() {
    this.editor.insertTable();
  }

  insertColumn() {
    this.onChange(
      this.editor.insertColumn()
    );
  }

  insertRow() {
    this.onChange(
      this.editor.insertRow()
    );
  }

  removeColumn() {
    this.onChange(
      this.editor.removeColumn()
    );
  }

  removeRow() {
    this.onChange(
      this.editor.removeRow()
    );
  }

  removeTable() {
    this.onChange(
      this.editor.removeTable()
    );
  }

  /* eslint-disable-next-line */
  renderNode(props, editor, next) {
    const { attributes, node, isFocused } = props;
    switch (node.type) {
      case 'equation':
        return <EquationEditor {...props} />;
      case 'image': {
        const src = node.data.get('src');
        return (
          <EditorImage
            isFocused={isFocused}
            src={src}
            {...attributes}
          />
        );
      }
      default:
        return next();
    }
  }

  render() {
    const {
      state: { value, activeTool },
      save,
      onChange,
      onMouseDown,
      renderNode,
      editor
    } = this;
    const inTable = editor && editor.isSelectionInTable(value);
    const { className } = this.props;
    return (
      <div className={className}>
        <Toolbar>
          <ToolbarLabel>Insert</ToolbarLabel>
          <ToolbarAction
            id={equation}
            onClick={() => { this.selectTool(equation); }}
            active={activeTool === equation}
          >
            <ToolbarIcon icon={{ icon: 'equal--small' }}>Equation</ToolbarIcon>
          </ToolbarAction>

          <ToolbarAction
            id={paragraph}
            onClick={() => { this.selectTool(paragraph); }}
            active={activeTool === paragraph}
          >
            <ToolbarIcon icon={{ icon: 'text-block' }}>Paragraph</ToolbarIcon>
          </ToolbarAction>

          <ToolbarAction
            id={table}
            onClick={() => { this.selectTool(table); }}
            active={activeTool === table}
          >
            <ToolbarIcon icon={{ icon: 'list' }}>Table</ToolbarIcon>
          </ToolbarAction>
          <ToolbarAction
            hidden={!inTable}
            onClick={this.insertColumn}
          >
           Add Column
          </ToolbarAction>
          <ToolbarAction
            hidden={!inTable}
            onClick={this.insertRow}
          >
            Add Row
          </ToolbarAction>
          <ToolbarAction
            hidden={!inTable}
            onClick={this.removeColumn}
          >
           Remove Column
          </ToolbarAction>
          <ToolbarAction
            hidden={!inTable}
            onClick={this.removeRow}
          >
            Remove Row
          </ToolbarAction>
          <ToolbarAction
            hidden={!inTable}
            onClick={this.removeTable}
          >
            Remove Table
          </ToolbarAction>
          <ToolbarAction onClick={save}>
            Save
          </ToolbarAction>

        </Toolbar>
        <EditorContainer>
          <Editor
            schema={schema}
            ref={editorValue => (this.editor = editorValue)}
            value={value}
            onChange={onChange}
            onMouseDown={onMouseDown}
            renderNode={renderNode}
            plugins={plugins}
          />
        </EditorContainer>
      </div>
    );
  }
}

FreeEditor.propTypes = {
  value: ImmutableTypes.record.isRequired,
  save: PropTypes.func.isRequired,
  className: PropTypes.string.isRequired
};

const StyledFreeEditor = styled(FreeEditor)`
  table {
    width: 100%;
    border-collapse: collapse;
    border-top: 1px solid ${themeVal('color.gray')};
    margin: ${themeVal('layout.space')} 0;
    table-layout: fixed;
  }
  table tr {
    border: none;
    border-bottom: 1px solid ${themeVal('color.gray')};
    border-right: 1px solid ${themeVal('color.gray')};
  }
  table thead tr {
    background: #f5f5f5;
    font-weight: bold;
  }
  table td {
    border: 1px solid ${themeVal('color.gray')};
    border-top: none;
    border-bottom: none;
    border-right: none;
    line-height: 1;
    padding: 0.5rem;
    position: relative;
  }
`;

export default StyledFreeEditor;
