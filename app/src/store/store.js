import {
  createStore,
  combineReducers,
  applyMiddleware
} from 'redux';
// import Immutable from 'immutable';
// import { composeWithDevTools } from 'redux-devtools-extension';
import thunk from 'redux-thunk';
import { apiMiddleware } from 'redux-api-middleware';
import reducer from '../reducers/reducer';

/*
const composeEnhancers = composeWithDevTools({
  serialize: {
    immutable: Immutable
  }
});
*/

const store = createStore(
  //combineReducers({
    //reducer
  //}),
  reducer,
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
