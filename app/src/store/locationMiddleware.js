import { LOCATION_CHANGE, push } from 'connected-react-router';
import * as actions from '../actions/actions';
import types from '../constants/action_types';
import {
  atbds,
  atbdsedit,
  identifying_information,
  introduction,
  contacts,
  drafts,
  algorithm_description,
  algorithm_usage,
  algorithm_implementation,
  error
} from '../constants/routes';

const locationMiddleware = store => next => async (action) => {
  const { type, payload } = action;
  if (type === LOCATION_CHANGE) {
    const { location: { pathname } } = payload;

    // Redirect '/' to '/atbds'
    if (pathname === '/') {
      return store.dispatch(push(`/${atbds}`));
    }

    const pathComponents = pathname.split('/');
    if (pathComponents[1] === atbds) {
      store.dispatch(actions.fetchAtbds());
    }
    if (pathComponents[1] === atbdsedit) {
      if (pathComponents[3] === drafts) {
        if (pathComponents[5] === algorithm_description || pathComponents[5] === introduction
          || pathComponents[5] === algorithm_usage || pathComponents[5] === identifying_information) {
          store.dispatch(actions.fetchAtbdVersion({
            atbd_id: pathComponents[2],
            atbd_version: pathComponents[4]
          }));
        }

        if (pathComponents[5] === contacts) {
          store.dispatch(actions.fetchAtbd(pathComponents[2]));
          store.dispatch(actions.fetchContacts());
          store.dispatch(actions.fetchContactGroups());
        }

        if (pathComponents[5] === algorithm_implementation) {
          store.dispatch(actions.fetchAlgorithmImplmentations({
            atbd_id: pathComponents[2],
            atbd_version: pathComponents[4]
          }));
        }

        if (pathComponents[5] === identifying_information) {
          store.dispatch(actions.fetchCitation({
            atbd_id: pathComponents[2],
            atbd_version: pathComponents[4]
          }));
        }
      }
    }

    // Fetch static json assets if undefined
    if (!store.getState().application.static) {
      store.dispatch(actions.fetchStatic());
    }
  }
  if (type === types.FETCH_ATBD_VERSION_FAIL) {
    store.dispatch(push(`/${error}`));
  }
  if (type === types.FETCH_ATBD_FAIL) {
    store.dispatch(push(`/${error}`));
  }

  if (type === types.CREATE_ATBD_SUCCESS) {
    const { created_version } = payload;
    const { atbd_id, atbd_version } = created_version;
    store.dispatch(push(`/${atbdsedit}/${atbd_id}/${drafts}/${atbd_version}/`
      + `${identifying_information}`));
  }
  return next(action);
};

export default locationMiddleware;
