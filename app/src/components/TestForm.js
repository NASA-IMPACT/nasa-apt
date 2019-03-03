import React from 'react';
import { connect } from 'react-redux';
import { withFormik } from 'formik';
import { Editor } from '@tinymce/tinymce-react';


const InnerTestForm = (props) => {
  const { values } = props;
  const { test } = values;
  return (
    <Editor
      initialValue={test}
      init={{
        skin_url: `${process.env.PUBLIC_URL}/skins/lightgray`,
        plugins: 'eqneditor',
        toolbar: 'eqneditor'
      }}
    />
  );
};

const TestForm = withFormik({
  mapPropsToValues: (props) => {
    const { test } = props;
    return { test };
  }
})(InnerTestForm);

const mapStateToProps = (state) => {
  const { test } = state;
  return { test };
};

export default connect(mapStateToProps)(TestForm);
