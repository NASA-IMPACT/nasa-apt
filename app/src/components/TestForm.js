import React from 'react';
import { connect } from 'react-redux';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import SectionEditor from './SectionEditor';
import schema from './editorSchema';
import { Button, Icon, Toolbar } from './Toolbars';
import { createAlgorithmDescription, fetchAlgorithmDescription } from '../actions/actions';

const plugins = [
  SoftBreak()
];

class TestForm extends React.Component {
  constructor(props) {
    super(props);
    const { algorithmDescription } = props;
    this.state = {
      value: algorithmDescription
    };
    this.onChange = this.onChange.bind(this);
    this.renderNode = this.renderNode.bind(this);
    this.insertEquation = this.insertEquation.bind(this);
    this.insertParagraph = this.insertParagraph.bind(this);
    this.save = this.save.bind(this);
  }

  componentDidMount() {
    const { fetchAlgorithmDescription: fetchDescription } = this.props;
    fetchDescription(1);
  }

  componentWillReceiveProps(nextProps) {
    const { algorithmDescription } = nextProps;
    this.setState({
      value: algorithmDescription
    });
  }

  onChange({ value }) {
    this.setState({ value });
  }

  save(e) {
    e.preventDefault();
    const { createAlgorithmDescription: create } = this.props;
    const jsonValue = this.editor.value.toJSON();
    const record = {
      data_model: jsonValue
    };
    create(record);
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

  renderNode(props, editor, next) {
    const { attributes, node, isFocused } = props;
    switch (node.type) {
      case 'equation':
        return <SectionEditor {...props} />;
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
    return (
      <div>
        <Toolbar>
          <Button onMouseDown={this.insertEquation}>
            <Icon>{'Equation'}</Icon>
          </Button>
          <Button onMouseDown={this.insertParagraph}>
            <Icon>{'Paragraph'}</Icon>
          </Button>
          <Button onMouseDown={this.save}>
            <Icon>{'Save'}</Icon>
          </Button>
        </Toolbar>
        <Editor
          ref={editor => (this.editor = editor)}
          schema={schema}
          value={this.state.value}
          onChange={this.onChange}
          renderNode={this.renderNode}
          plugins={plugins}
        />
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  const { algorithmDescription } = state;
  return { algorithmDescription };
};

const mapDispatchToProps = {
  createAlgorithmDescription,
  fetchAlgorithmDescription
};

export default connect(mapStateToProps, mapDispatchToProps)(TestForm);
