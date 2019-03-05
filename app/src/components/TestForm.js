import React from 'react';
import { connect } from 'react-redux';
import { Editor } from 'slate-react';
import SectionEditor from './SectionEditor';
import schema from './editorSchema';

class TestForm extends React.Component {
  constructor(props) {
    super(props);
    const { test } = props;
    this.state = {
      value: test
    };
    this.onChange = this.onChange.bind(this);
    this.renderNode = this.renderNode.bind(this);
  }

  onChange({ value }) {
    this.setState({ value });
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
      <Editor
        schema={schema}
        value={this.state.value}
        onChange={this.onChange}
        renderNode={this.renderNode}
      />
    );
  }
}

const mapStateToProps = (state) => {
  const { test } = state;
  return { test };
};

export default connect(mapStateToProps)(TestForm);
