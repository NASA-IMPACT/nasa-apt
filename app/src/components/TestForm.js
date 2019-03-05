import React from 'react';
import { connect } from 'react-redux';
import { Editor } from 'slate-react';
import SoftBreak from 'slate-soft-break';
import SectionEditor from './SectionEditor';
import schema from './editorSchema';
import { Button, Icon, Toolbar } from './Toolbars';

const plugins = [
  SoftBreak()
];

class TestForm extends React.Component {
  constructor(props) {
    super(props);
    const { test } = props;
    this.state = {
      value: test
    };
    this.onChange = this.onChange.bind(this);
    this.renderNode = this.renderNode.bind(this);
    this.insertEquation = this.insertEquation.bind(this);
  }

  onChange({ value }) {
    this.setState({ value });
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
  const { test } = state;
  return { test };
};

export default connect(mapStateToProps)(TestForm);
