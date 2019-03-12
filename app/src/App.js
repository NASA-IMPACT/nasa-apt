import React from 'react';
import { Provider } from 'react-redux';
import GlobalStyle from './styles/global';
import createStore from './store/store';
import ContactForm from './components/ContactForm';
import AlgorithmDescriptionForm from './components/AlgorithmDescriptionForm';

const store = createStore;

const App = () => (
  <Provider store={store}>
    <GlobalStyle />
    <ContactForm />
    <AlgorithmDescriptionForm />
  </Provider>
);

export default App;
