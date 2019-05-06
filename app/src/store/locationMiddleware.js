import { LOCATION_CHANGE, push } from 'connected-react-router';
import * as actions from '../actions/actions';
import types from '../constants/action_types';
import {
  atbds,
  atbdsedit,
  identifying_information,
  contacts,
  drafts,
  algorithm_description,
  algorithm_implementation,
  error
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
      if (pathComponents[3] === drafts) {
        const versionObject = {
          atbd_id: pathComponents[2],
          atbd_version: pathComponents[4]
        };

        // Version variables and algorithm implementations
        // queries both include the atbd version in their query.
        if (pathComponents[5] === algorithm_description) {
          store.dispatch(actions.fetchAtbdVersionVariables(versionObject));
        } else if (pathComponents[5] === algorithm_implementation) {
          store.dispatch(actions.fetchAlgorithmImplmentations(versionObject));
        } else {
          store.dispatch(actions.fetchAtbdVersion(versionObject));
        }

        if (pathComponents[5] === contacts) {
          store.dispatch(actions.fetchAtbd(pathComponents[2]));
          store.dispatch(actions.fetchContacts());
          store.dispatch(actions.fetchContactGroups());
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
