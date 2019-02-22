import {
  createStore,
  combineReducers,
  applyMiddleware
} from 'redux';
// import Immutable from 'immutable';
// import { composeWithDevTools } from 'redux-devtools-extension';
import thunk from 'redux-thunk';
import reducer from '../reducers/reducer';
import apiMiddleware from './apiMiddleware';

/*
const composeEnhancers = composeWithDevTools({
  serialize: {
    immutable: Immutable
  }
});
*/

const initialState = {};
const store = createStore(
  combineReducers({
    reducer
  }),
  initialState,
  applyMiddleware(
    thunk,
    apiMiddleware
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
