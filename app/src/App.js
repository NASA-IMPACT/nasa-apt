import React from 'react';
import { Provider } from 'react-redux';
import { Route, Switch } from 'react-router';
import { ConnectedRouter } from 'connected-react-router';

import styled, { ThemeProvider } from 'styled-components';
import theme from './styles/theme/theme';
import GlobalStyle from './styles/global';

import store, { history } from './store/store';
import {
  atbds,
  atbdsedit,
  introduction,
  contacts,
  drafts,
  algorithm_description,
  algorithm_usage
} from './constants/routes';
import PageHeader from './components/common/PageHeader';
import PageFooter from './components/common/PageFooter';
import AtbdList from './components/AtbdList';
import Introduction from './components/Introduction';
import Contacts from './components/Contacts';
import AlgorithmDescription from './components/AlgorithmDescription';
import AlgorithmUsage from './components/AlgorithmUsage';
import Help from './components/help';
import About from './components/about';
import Sandbox from './components/sandbox';
import UhOh from './components/uhoh';

const Page = styled.div`
  display: grid;
  min-height: 100vh;
  grid-template-rows: auto 1fr auto;
`;

const PageBody = styled.main`
  padding: 0;
  margin: 0;
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
                <Route path={`/${atbds}`} component={AtbdList} />
                <Route
                  path={`/${atbdsedit}/:atbd_id/${drafts}/:atbd_version/${introduction}`}
                  component={Introduction}
                />
                <Route
                  path={`/${atbdsedit}/:atbd_id/${contacts}`}
                  component={Contacts}
                />
                <Route
                  path={`/${atbdsedit}/:atbd_id/${drafts}/:atbd_version/${algorithm_description}`}
                  component={AlgorithmDescription}
                />
                <Route
                  path={`/${atbdsedit}/:atbd_id/${drafts}/:atbd_version/${algorithm_usage}`}
                  component={AlgorithmUsage}
                />
                <Route exact path="/help" component={Help} />
                <Route exact path="/about" component={About} />
                <Route exact path="/sandbox" component={Sandbox} />
                <Route path="*" component={UhOh} />
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
