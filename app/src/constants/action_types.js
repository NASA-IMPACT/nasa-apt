import { createTypes, async } from 'redux-action-creator';

const types = createTypes([
  ...async('CREATE_CONTACT'),
  ...async('CREATE_CONTACT_GROUP'),
  ...async('CREATE_ATBD'),
  ...async('CREATE_ATBD_VERSION'),
  ...async('UPDATE_ATBD_VERSION'),
  ...async('FETCH_ATBD_VERSION'),
  ...async('UPDATE_PERFORMANCE_ASSESSMENT'),
  ...async('CREATE_PERFORMANCE_ASSESSMENT'),
  ...async('FETCH_ATBDS'),
  ...async('FETCH_ATBD'),
  ...async('FETCH_CONTACTS'),
  ...async('CREATE_ATBD_CONTACT'),
  ...async('DELETE_ATBD_CONTACT'),
  ...async('FETCH_CONTACT_GROUPS'),
  ...async('CREATE_ATBD_CONTACT_GROUP'),
  ...async('DELETE_ATBD_CONTACT_GROUP'),
  ...async('CREATE_ALGORITHM_INPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_INPUT_VARIABLE'),
  ...async('CREATE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('FETCH_ALGORITHM_IMPLEMENTATION'),
  ...async('CREATE_ALGORITHM_IMPLEMENTATION'),
  ...async('UPDATE_ALGORITHM_IMPLEMENTATION'),
  ...async('DELETE_ALGORITHM_IMPLEMENTATION'),
  ...async('UPLOAD_FILE'),
  ...async('FETCH_STATIC')
]);

export default types;
