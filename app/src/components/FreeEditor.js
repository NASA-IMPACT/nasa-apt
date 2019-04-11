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
  EquationBtn,
  ParagraphBtn,
  TableBtn,
  Toolbar,
  ToolbarLabel
} from './Toolbars';
import EditorImage from './EditorImage';
import EditorTable from './EditorTable';
import EditorFormattableText from './EditorFormattableText';
import schema from './editorSchema';
import { themeVal } from '../styles/utils/general';
import { multiply } from '../styles/utils/math';
import Strong from '../styles/atoms/Strong';
import Button from '../styles/atoms/button';
import ButtonGroup from '../styles/molecules/button-group';

const equation = 'equation';
const paragraph = 'paragraph';
const table = 'table';

const EditorContainer = styled.div`
  background-color: ${themeVal('color.surface')};
  border: 1px solid ${themeVal('color.gray')};
  border-bottom-left-radius: ${multiply(themeVal('layout.space'), 0.25)};
  border-bottom-right-radius: ${multiply(themeVal('layout.space'), 0.25)};
  padding: 1rem 3rem;
`;

const plugins = [
  TrailingBlock(),
  SoftBreak(),
  PluginDeepTable()
];

function renderMark(props, editor, next) {
  const {
    mark: { type },
    children
  } = props;
  switch (type) {
    case 'bold': {
      return <Strong {...props}>{children}</Strong>;
    }
    case 'italic': {
      return <em {...props}>{children}</em>;
    }
    case 'underline': {
      return <u {...props}>{children}</u>;
    }
    case 'strikethrough': {
      return <s {...props}>{children}</s>;
    }
    default: {
      return next();
    }
  }
}

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
    this.onKeyDown = this.onKeyDown.bind(this);
    this.toggleMark = this.toggleMark.bind(this);
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

  onKeyDown(event, editor, next) {
    if (!event.metaKey) return next();

    let nextMark;
    switch (event.key) {
      case 'b': {
        nextMark = 'bold';
        break;
      }
      case 'i': {
        nextMark = 'italic';
        break;
      }
      case 'u': {
        nextMark = 'underline';
        break;
      }
      default: {
        return next();
      }
    }

    if (nextMark) {
      event.preventDefault();
      this.toggleMark(nextMark);
    }
  }

  onChange(event) {
    const { value } = event;
    this.setState({
      value,
      activeTool: null
    });
  }

  toggleMark(nextMark) {
    this.editor.toggleMark(nextMark);
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

  renderNode(props, editor, next) {
    const { attributes, node, isFocused } = props;
    const { value } = this.state;
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
      case 'table': {
        return (
          <EditorTable
            remove={this.removeTable}
            insertRow={this.insertRow}
            removeRow={this.removeRow}
            insertColumn={this.insertColumn}
            removeColumn={this.removeColumn}
            {...props}
          />
        );
      }
      case 'paragraph': {
        // Focus text applies when a single text block is focused.
        // Importantly, it's empty when multiple, non-text blocks are focused.
        // Use focus text in addition to the length of any highlighted text
        // to determine whether we have a selection.
        const focusText = value.focusText ? value.focusText.text : '';
        const selectedText = value.fragment.text;
        const hasSelection = !!(focusText.length && selectedText.length);
        const activeMarks = Array.from(value.activeMarks)
          .map(Mark => Mark.type);
        return (
          <EditorFormattableText
            hasSelection={hasSelection}
            activeMarks={activeMarks}
            toggleMark={this.toggleMark}
            {...props}
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
      onKeyDown,
      renderNode
    } = this;
    const { className } = this.props;
    return (
      <div className={className}>
        <Toolbar>
          <ButtonGroup orientation="horizontal">
            <ToolbarLabel>Insert</ToolbarLabel>
            <EquationBtn
              id={equation}
              onClick={() => { this.selectTool(equation); }}
              active={activeTool === equation}
              variation="base-plain"
              size="large"
            >
              Equation
            </EquationBtn>

            <ParagraphBtn
              id={paragraph}
              onClick={() => { this.selectTool(paragraph); }}
              active={activeTool === paragraph}
              variation="base-plain"
              size="large"
            >
              Paragraph
            </ParagraphBtn>

            <TableBtn
              id={table}
              onClick={() => { this.selectTool(table); }}
              active={activeTool === table}
              variation="base-plain"
              size="large"
            >
              Table
            </TableBtn>
            <Button
              onClick={save}
              variation="base-plain"
              size="large"
            >
              Save
            </Button>
          </ButtonGroup>
        </Toolbar>
        <EditorContainer>
          <Editor
            schema={schema}
            ref={editorValue => (this.editor = editorValue)}
            value={value}
            onChange={onChange}
            onMouseDown={onMouseDown}
            onKeyDown={onKeyDown}
            renderNode={renderNode}
            renderMark={renderMark}
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
    margin-bottom: ${themeVal('layout.space')};
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
