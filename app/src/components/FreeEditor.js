import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Value } from 'slate';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import PluginDeepTable from 'slate-deep-table';
import styled from 'styled-components/macro';
import { rgba } from 'polished';
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
import EditorFigureTool from './EditorFigureTool';
import EditorReference from './EditorReference';
import EditorReferenceTool from './EditorReferenceTool';
import EditorFormattableText from './EditorFormattableText';
import EditorInlineMetadata from './EditorInlineMetadata';
import { getValidOrBlankDocument } from './editorBlankDocument';
import schema from './editorSchema';
import { themeVal, stylizeFunction } from '../styles/utils/general';
import { multiply } from '../styles/utils/math';
import Button from '../styles/button/button';
import ButtonGroup from '../styles/button/group';

const equation = 'equation';
const paragraph = 'paragraph';
const table = 'table';
const image = 'image';
const reference = 'reference';

const _rgba = stylizeFunction(rgba);

const EditorStatus = styled.div`
  border-color: ${props => (props.invalid ? themeVal('color.danger')
    : _rgba(themeVal('color.base'), 0.16))};
  border-radius: ${themeVal('shape.rounded')};
  border-style: solid;
  border-width: ${props => (props.invalid ? multiply(themeVal('layout.border'), 2)
    : themeVal('layout.border'))};
  margin-bottom: 1rem;
`;

const EditorContainer = styled.div`
  background-color: ${themeVal('color.surface')};
  border-bottom-left-radius: ${themeVal('shape.rounded')};
  border-bottom-right-radius: ${themeVal('shape.rounded')};
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
      return <strong {...props}>{children}</strong>;
    }
    case 'italic': {
      return <em {...props}>{children}</em>;
    }
    case 'underline': {
      return <u {...props}>{children}</u>;
    }
    default: {
      return next();
    }
  }
}

export class FreeEditor extends React.Component {
  constructor(props) {
    super(props);
    const { initialValue } = props;
    this.state = {
      value: Value.fromJSON(getValidOrBlankDocument(initialValue)),
      activeTool: null,
      uploadedImageToPlace: null,
      uploadedImageCaption: null
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
    this.insertImage = this.insertImage.bind(this);
    this.insertLink = this.insertLink.bind(this);
    this.insertReference = this.insertReference.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    const {
      initialValue
    } = nextProps;
    const {
      initialValue: previousInitialValue
    } = this.props;

    if (initialValue !== previousInitialValue) {
      this.setState({
        value: Value.fromJSON(getValidOrBlankDocument(initialValue))
      });
    }
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
        if (activeTool === image) {
          this.insertImage();
        }
        if (activeTool === reference) {
          this.insertReference();
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

  insertImage() {
    const {
      uploadedImageToPlace: src,
      uploadedImageCaption: caption
    } = this.state;
    this.editor.insertBlock({
      type: 'image',
      data: {
        src,
        caption
      }
    }).insertBlock({
      type: paragraph,
      nodes: [
        {
          object: 'text',
          leaves: [{
            text: '',
          }]
        },
      ],
    });
  }

  insertLink(url, replaceText) {
    const { value } = this.state;
    const { selection } = value;
    let text = replaceText;
    if (!text) {
      text = selection.isCollapsed ? 'link' : value.fragment.text;
    }
    this.editor.insertInline({
      type: 'link',
      data: { url },
      nodes: [{
        object: 'text',
        leaves: [{
          text
        }]
      }]
    });
  }

  insertReference() {
    const { lastCreatedReference } = this.props;
    const {
      publication_reference_id: id,
      title: name
    } = lastCreatedReference;
    this.editor.insertInline({
      type: reference,
      data: { id, name },
      nodes: [{
        object: 'text',
        leaves: [{
          // TODO: decide if we want to render something
          // more meaningful than this stand-in.
          text: 'ref'
        }]
      }]
    });
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
    const {
      attributes,
      children,
      node,
      isFocused
    } = props;
    const { value } = this.state;
    const selectedText = value.fragment.text;

    switch (node.type) {
      case 'equation':
        return <EquationEditor {...props} />;
      case 'image': {
        const src = node.data.get('src');
        const caption = node.data.get('caption');
        return (
          <figure>
            <EditorImage
              isFocused={isFocused}
              src={src}
              {...attributes}
            />
            <figcaption>{caption}</figcaption>
          </figure>
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

        // The reason we must check whether the value fragment exists
        // in the focused text is because focusing on an inline fragment,
        // ie a link or reference, will trigger this case as well as
        // the case for that specific inline node.
        const hasSelection = !!(focusText.length && selectedText.length
          && focusText.indexOf(selectedText) >= 0);

        const activeMarks = Array.from(value.activeMarks)
          .map(Mark => Mark.type);

        return (
          <EditorFormattableText
            hasSelection={hasSelection}
            activeMarks={activeMarks}
            toggleMark={this.toggleMark}
            insertLink={this.insertLink}
            {...props}
          />
        );
      }

      case 'link': {
        const url = node.data.get('url');
        return (
          <EditorInlineMetadata
            hasActiveSelection={!!(selectedText.length && url)}
            metadata={url}
            readOnly
          >
            <a href={url} rel="noopener noreferrer" target="_blank" {...attributes}>{children}</a>
          </EditorInlineMetadata>
        );
      }

      case reference: {
        const name = node.data.get('name');
        return (
          <EditorInlineMetadata
            hasActiveSelection={!!(selectedText.length && name)}
            metadata={`Ref: ${name}`}
            readOnly
          >
            <EditorReference
              data-reference-id={node.data.get('id')}
              {...attributes}
            >
              {children}
            </EditorReference>
          </EditorInlineMetadata>
        );
      }
      default:
        return next();
    }
  }

  render() {
    const {
      state: {
        value,
        activeTool
      },
      save,
      onChange,
      onMouseDown,
      onKeyDown,
      renderNode
    } = this;

    const {
      className,
      inlineSaveBtn,
      invalid
    } = this.props;

    return (
      <div className={className}>
        <EditorStatus invalid={invalid}>
          <Toolbar>
            <ToolbarLabel>Insert</ToolbarLabel>
            <ButtonGroup orientation="horizontal">
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

              <EditorFigureTool
                onSaveSuccess={(uploadedFile, caption) => {
                  this.setState({
                    uploadedImageToPlace: uploadedFile,
                    uploadedImageCaption: caption
                  }, () => this.selectTool(image));
                }}
                active={activeTool === image}
              />

              <EditorReferenceTool
                onSaveSuccess={() => { this.selectTool(reference); }}
                active={activeTool === reference}
              />

              {inlineSaveBtn && (
                <Button
                  onClick={save}
                  variation="base-plain"
                  size="large"
                >
                  Save
                </Button>
              )}
            </ButtonGroup>
          </Toolbar>
          <EditorContainer>
            <Editor
              ref={editorValue => (this.editor = editorValue)}
              schema={schema}
              value={value}
              onChange={onChange}
              onMouseDown={onMouseDown}
              onKeyDown={onKeyDown}
              renderNode={renderNode}
              renderMark={renderMark}
              plugins={plugins}
            />
          </EditorContainer>
        </EditorStatus>
        {!inlineSaveBtn && (
          <Button
            onClick={save}
            variation="base-raised-light"
            size="large"
          >
            Save
          </Button>
        )}
      </div>
    );
  }
}

FreeEditor.propTypes = {
  initialValue: PropTypes.object,
  save: PropTypes.func.isRequired,
  className: PropTypes.string,
  lastCreatedReference: PropTypes.object,
  inlineSaveBtn: PropTypes.bool,
  invalid: PropTypes.bool
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

const mapStateToProps = (state) => {
  const { lastCreatedReference } = state.application;
  return { lastCreatedReference };
};

export default connect(mapStateToProps, null)(StyledFreeEditor);
