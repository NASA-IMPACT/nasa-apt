import React from 'react';
import PropTypes from 'prop-types';
import ImmutableTypes from 'react-immutable-proptypes';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import PluginDeepTable from 'slate-deep-table';
import styled from 'styled-components/macro';
import EquationEditor from './EquationEditor';
import {
  ToolbarAction,
  ToolbarIcon,
  Toolbar,
  ToolbarLabel
} from './Toolbars';
import EditorImage from './EditorImage';
import schema from './editorSchema';

const equation = 'equation';
const paragraph = 'paragraph';
const table = 'table';

const plugins = [
  SoftBreak(),
  PluginDeepTable()
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
    this.setState({
      activeTool: tool
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
    this.insertParagraph();
    this.editor.moveBackward(1);
    this.editor.insertTable();
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
    } = this;
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
            <ToolbarIcon icon={{ icon: 'list'}}>Table</ToolbarIcon>
          </ToolbarAction>

          <ToolbarAction onClick={save}>
            Save
          </ToolbarAction>

        </Toolbar>
        <Editor
          schema={schema}
          ref={editor => (this.editor = editor)}
          value={value}
          onChange={onChange}
          onMouseDown={onMouseDown}
          renderNode={renderNode}
          plugins={plugins}
        />
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
    border-top: 1px solid black;
  }
  table tr {
    border: none;
    border-bottom: 1px solid black;
    border-right: 1px solid black;
  }
  table thead tr {
    background: #f5f5f5;
    font-weight: bold;
  }
  table td {
    border: 1px solid black;
    border-top: none;
    border-bottom: none;
    border-right: none;
    padding: .5em;
    position: relative;
  }
`;

export default StyledFreeEditor;
