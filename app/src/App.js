import React from 'react';
import { Provider } from 'react-redux';

import styled, { css } from 'styled-components';
import { ThemeProvider } from 'styled-components';
import theme from './styles/theme/theme';
import GlobalStyle from './styles/global';

import createStore from './store/store';
import ContactForm from './components/ContactForm';
import PageHeader from './components/common/PageHeader';
import AlgorithmDescriptionForm from './components/AlgorithmDescriptionForm';

const store = createStore;

const Page = styled.div`
  display: grid;
`;

const App = () => (
  <Provider store={store}>
    <ThemeProvider theme={theme.main}>
      <React.Fragment>
        <GlobalStyle />
        <Page>
          <PageHeader />
          <ContactForm />
          <AlgorithmDescriptionForm />
        </Page>
      </React.Fragment>
    </ThemeProvider>
  </Provider>
);

export default App;
