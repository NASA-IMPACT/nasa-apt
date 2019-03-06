import React from 'react';
import { Provider } from 'react-redux';
/* eslint-disable-next-line */
import createStore from './store/store';
import ContactForm from './components/ContactForm';
import AlgorithmDescriptionForm from './components/AlgorithmDescriptionForm';

const store = createStore;

const App = () => (
  <Provider store={store}>
    <ContactForm />
    <AlgorithmDescriptionForm />
  </Provider>
);

export default App;
