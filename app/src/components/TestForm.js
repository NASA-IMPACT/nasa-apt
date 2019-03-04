import React from 'react';
import { connect } from 'react-redux';
import { Editor } from 'slate-react';
import 'katex/dist/katex.min.css';
import { InlineMath } from 'react-katex';

class TestForm extends React.Component {
  constructor(props) {
    super(props);
    const { test } = props;
    this.state = {
      value: test
    };
    this.onChange = this.onChange.bind(this);
    this.renderMark = this.renderMark.bind(this);
  }

  onChange({ value }) {
    this.setState({ value });
  }

  renderMark(props, editor, next) {
    switch (props.mark.type) {
      case 'latex':
        return <InlineMath math={props.text} />;
      default:
        return next();
    }
  }

  render() {
    return (
      <Editor
        value={this.state.value}
        onChange={this.onChange}
        renderMark={this.renderMark}
      />
    );
  }
}

const mapStateToProps = (state) => {
  const { test } = state;
  return { test };
};

export default connect(mapStateToProps)(TestForm);
