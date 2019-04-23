import { createTypes, async } from 'redux-action-creator';

const types = createTypes([
  ...async('CREATE_CONTACT'),
  ...async('CREATE_ATBD'),
  ...async('CREATE_ATBD_VERSION'),
  ...async('UPDATE_ATBD_VERSION'),
  ...async('FETCH_ATBD_VERSION'),
  ...async('FETCH_ATBD_VERSION_PERFORMANCE_ASSESSMENT'),
  ...async('UPDATE_PERFORMANCE_ASSESSMENT'),
  ...async('CREATE_PERFORMANCE_ASSESSMENT'),
  ...async('FETCH_ATBDS'),
  ...async('FETCH_ATBD'),
  ...async('FETCH_CONTACTS'),
  ...async('CREATE_ATBD_CONTACT'),
  ...async('DELETE_ATBD_CONTACT'),
  ...async('CREATE_ALGORITHM_INPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_INPUT_VARIABLE'),
  ...async('CREATE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('UPLOAD_FILE')
]);

export default types;
