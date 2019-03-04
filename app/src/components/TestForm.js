import React from 'react';
import { connect } from 'react-redux';
import { Editor } from 'slate-react';

class TestForm extends React.Component {
  constructor(props) {
    super(props);
    const { test } = props;
    this.state = {
      value: test
    };
    this.onChange = this.onChange.bind(this);
  }

  onChange({ value }) {
    this.setState({ value });
  }

  render() {
    return <Editor value={this.state.value} onChange={this.onChange} />;
  }
}

const mapStateToProps = (state) => {
  const { test } = state;
  return { test };
};

export default connect(mapStateToProps)(TestForm);
