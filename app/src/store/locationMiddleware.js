import { LOCATION_CHANGE } from 'connected-react-router';
import * as routes from '../constants/routes';
import * as actions from '../actions/actions';

const locationMiddleware = store => next => async (action) => {
  const { type, payload } = action;
  if (type === LOCATION_CHANGE) {
    const { location: { pathname } } = payload;
    const pathComponents = pathname.split('/');
    if (pathComponents[1] === routes.atbds) {
      store.dispatch(actions.fetchAtbds());
    }
    if (pathComponents[1] === routes.atbdsedit) {
      if (pathComponents[2]) {
        store.dispatch(actions.fetchAtbd(pathComponents[2]));
        store.dispatch(actions.fetchContacts());
      }
    }
  }
  return next(action);
};

export default locationMiddleware;
