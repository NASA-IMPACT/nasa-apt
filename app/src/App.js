import React from 'react';
import { Provider } from 'react-redux';
import { Route, Switch } from 'react-router';
import { ConnectedRouter } from 'connected-react-router';

import styled from 'styled-components';
import { ThemeProvider } from 'styled-components';
import theme from './styles/theme/theme';
import GlobalStyle from './styles/global';
import { themeVal } from './styles/utils/general';

import store, { history } from './store/store';
import * as routes from './constants/routes';
import ContactForm from './components/ContactForm';
import PageHeader from './components/common/PageHeader';
import PageFooter from './components/common/PageFooter';
import AtbdList from './components/AtbdList';
import AlgorithmDescriptionForm from './components/AlgorithmDescriptionForm';

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
    <ConnectedRouter history={history}>
      <ThemeProvider theme={theme.main}>
        <React.Fragment>
          <GlobalStyle />
          <Page>
            <PageHeader />
            <PageBody>
              <Switch>
                <Route path={`/${routes.atbds}`} component={AtbdList} />
                <Route path={`/${routes.atbdsedit}/:atbd_id`} component={AtbdList} />
              </Switch>
            </PageBody>
            <PageFooter />
          </Page>
        </React.Fragment>
      </ThemeProvider>
    </ConnectedRouter>
  </Provider>
);

export default App;
