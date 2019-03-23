import { LOCATION_CHANGE } from 'connected-react-router';
import * as actions from '../actions/actions';
import {
  atbds,
  atbdsedit,
  contacts,
  versions,
  algorithm_description
} from '../constants/routes';

const locationMiddleware = store => next => async (action) => {
  const { type, payload } = action;
  if (type === LOCATION_CHANGE) {
    const { location: { pathname } } = payload;
    const pathComponents = pathname.split('/');
    if (pathComponents[1] === atbds) {
      store.dispatch(actions.fetchAtbds());
    }
    if (pathComponents[1] === atbdsedit) {
      if (pathComponents[3] === contacts) {
        store.dispatch(actions.fetchAtbd(pathComponents[2]));
        store.dispatch(actions.fetchContacts());
      }
      if (pathComponents[3] === versions) {
        if (pathComponents[5] === algorithm_description) {
          store.dispatch(actions.fetchAtbdVersion({
            atbd_id: pathComponents[2],
            atbd_version: pathComponents[4]
          }));
        }
      }
    }
  }
  return next(action);
};

export default locationMiddleware;
