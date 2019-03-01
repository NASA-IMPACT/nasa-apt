import React from 'react';
import { Provider } from 'react-redux';
import tinymce from 'tinymce/tinymce';
import 'tinymce/plugins/paste';
import 'tinymce/plugins/link';
import 'tinymce/plugins/code';
import 'tinymce/themes/modern';
import createStore from './store/store';
import ContactForm from './components/ContactForm';
import TestForm from './components/TestForm';

tinymce.init({
  selector: '#tiny',
});
const store = createStore;

const App = () => (
  <Provider store={store}>
    <ContactForm />
    <TestForm />
  </Provider>
);

export default App;
