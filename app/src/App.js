import React from 'react';
import { Provider } from 'react-redux';
/* eslint-disable-next-line */
import createStore from './store/store';
import ContactForm from './components/ContactForm';
import TestForm from './components/TestForm';

const store = createStore;

const App = () => (
  <Provider store={store}>
    <ContactForm />
    <TestForm />
  </Provider>
);

export default App;
