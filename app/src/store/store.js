import {
  createStore,
  combineReducers,
  applyMiddleware
} from 'redux';
// import { composeWithDevTools } from 'redux-devtools-extension';
import thunk from 'redux-thunk';
import { apiMiddleware } from 'redux-api-middleware';
import { createBrowserHistory } from 'history';
import { connectRouter, routerMiddleware } from 'connected-react-router';
import reducer from '../reducers/reducer';
import locationMiddleware from './locationMiddleware';
/*
const composeEnhancers = composeWithDevTools({
  serialize: {
    immutable: Immutable
  }
});
*/
export const history = createBrowserHistory();
const store = createStore(
  combineReducers({
    router: connectRouter(history),
    application: reducer
  }),
  applyMiddleware(
    routerMiddleware(history),
    thunk,
    apiMiddleware,
    locationMiddleware
  )
  /*
  composeEnhancers(
    applyMiddleware(
      thunk,
      apiMiddleware
    )
  )
  */
);

export default store;
