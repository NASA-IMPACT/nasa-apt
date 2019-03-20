import React from 'react';
import { Provider } from 'react-redux';

import styled, { css } from 'styled-components';
import { ThemeProvider } from 'styled-components';
import theme from './styles/theme/theme';
import GlobalStyle from './styles/global';
import { themeVal } from './styles/utils/general';

import createStore from './store/store';
import ContactForm from './components/ContactForm';
import PageHeader from './components/common/PageHeader';
import PageFooter from './components/common/PageFooter';
import AlgorithmDescriptionForm from './components/AlgorithmDescriptionForm';

const store = createStore;

const Page = styled.div`
  display: grid;
  min-height: 100vh;
  grid-auto-rows: auto 1fr auto;
`;

const PageBody = styled.main`
  padding: ${themeVal('layout.space')};
`;

const App = () => (
  <Provider store={store}>
    <ThemeProvider theme={theme.main}>
      <React.Fragment>
        <GlobalStyle />
        <Page>
          <PageHeader />
          <PageBody>
            <ContactForm />
            <AlgorithmDescriptionForm />
          </PageBody>
          <PageFooter />
        </Page>
      </React.Fragment>
    </ThemeProvider>
  </Provider>
);

export default App;
