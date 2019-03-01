import React from 'react';
import { Editor } from '@tinymce/tinymce-react';

const TestForm = () => (
  <Editor
    initialValue="<p>This is the initial content of the editor</p>"
    init={{
      skin_url: `${process.env.PUBLIC_URL}/skins/lightgray`,
      plugins: 'code',
      toolbar: 'code'
    }}
  />
);

export default TestForm;
