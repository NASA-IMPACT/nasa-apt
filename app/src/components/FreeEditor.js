import React from 'react';
import PropTypes from 'prop-types';
import ImmutableTypes from 'react-immutable-proptypes';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import EquationEditor from './EquationEditor';
import schema from './editorSchema';
import { Button, Icon, Toolbar } from './Toolbars';

const plugins = [
  SoftBreak()
];

class FreeEditor extends React.Component {
  constructor(props) {
    super(props);
    const { value } = props;
    this.state = { value };
    this.onChange = this.onChange.bind(this);
    this.renderNode = this.renderNode.bind(this);
    this.insertEquation = this.insertEquation.bind(this);
    this.insertParagraph = this.insertParagraph.bind(this);
    this.save = this.save.bind(this);
  }

  componentDidMount() {
    const { fetchDocument } = this.props;
    fetchDocument(1);
  }

  componentWillReceiveProps(nextProps) {
    const { value } = nextProps;
    this.setState({ value });
  }

  onChange({ value }) {
    this.setState({ value });
  }

  save(e) {
    e.preventDefault();
    const { createDocument } = this.props;
    const jsonValue = this.editor.value.toJSON();
    const record = {
      data_model: jsonValue
    };
    createDocument(record);
  }

  insertEquation(e) {
    e.preventDefault();
    this.editor
      .insertBlock({
        type: 'equation',
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

  insertParagraph(e) {
    e.preventDefault();
    this.editor
      .insertBlock({
        type: 'paragraph',
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

  /* eslint-disable-next-line */
  renderNode(props, editor, next) {
    const { attributes, node, isFocused } = props;
    switch (node.type) {
      case 'equation':
        return <EquationEditor {...props} />;
      case 'image': {
        const imageClass = {
          display: 'block',
          maxWidth: '100%',
          maxHeight: '20em',
          boxShadow: isFocused ? '0 0 0 2px blue' : 'none'
        };
        const src = node.data.get('src');
        return <img src={src} style={imageClass} {...attributes} />;
      }
      default:
        return next();
    }
  }

  render() {
    const {
      state: { value },
      insertEquation,
      insertParagraph,
      save,
      onChange,
      renderNode
    } = this;

    return (
      <div>
        <Toolbar>
          <Button onMouseDown={insertEquation}>
            <Icon>Equation</Icon>
          </Button>
          <Button onMouseDown={insertParagraph}>
            <Icon>Paragraph</Icon>
          </Button>
          <Button onMouseDown={save}>
            <Icon>Save</Icon>
          </Button>
        </Toolbar>
        <Editor
          ref={editor => (this.editor = editor)}
          schema={schema}
          value={value}
          onChange={onChange}
          renderNode={renderNode}
          plugins={plugins}
        />
      </div>
    );
  }
}

FreeEditor.propTypes = {
  value: ImmutableTypes.record.isRequired,
  createDocument: PropTypes.func.isRequired,
  fetchDocument: PropTypes.func.isRequired
};

export default FreeEditor;
