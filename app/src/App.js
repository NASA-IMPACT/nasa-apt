import React from 'react';
import { Provider } from 'react-redux';
import createStore from './store/store';
import ContactForm from './components/ContactForm';

const store = createStore;

const App = () => (
  <Provider store={store}>
    <ContactForm />
  </Provider>
);

export default App;
