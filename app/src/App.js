import React from 'react';
import { Provider } from 'react-redux';
import createStore from './store/store';

const store = createStore;

const App = () => (
  <Provider store={store}>
    <span>Wat</span>
  </Provider>
);

export default App;
