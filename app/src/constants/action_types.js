import { createTypes, async } from 'redux-action-creator';

const types = createTypes([
  ...async('CREATE_CONTACT'),
  ...async('UPDATE_CONTACT'),
  ...async('CREATE_CONTACT_GROUP'),
  ...async('UPDATE_CONTACT_GROUP'),
  ...async('CREATE_ATBD'),
  ...async('UPDATE_ATBD'),
  ...async('CREATE_ATBD_VERSION'),
  ...async('UPDATE_ATBD_VERSION'),
  ...async('FETCH_ATBD_VERSION'),
  ...async('UPDATE_PERFORMANCE_ASSESSMENT'),
  ...async('CREATE_PERFORMANCE_ASSESSMENT'),
  ...async('FETCH_ATBDS'),
  ...async('FETCH_ATBD'),
  ...async('FETCH_CITATIONS'),
  ...async('CREATE_CITATION'),
  ...async('UPDATE_CITATION'),
  ...async('FETCH_CONTACTS'),
  ...async('CREATE_ATBD_CONTACT'),
  ...async('DELETE_ATBD_CONTACT'),
  ...async('FETCH_CONTACT_GROUPS'),
  ...async('CREATE_ATBD_CONTACT_GROUP'),
  ...async('DELETE_ATBD_CONTACT_GROUP'),
  ...async('FETCH_ALGORITHM_VARIABLES'),
  ...async('CREATE_ALGORITHM_INPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_INPUT_VARIABLE'),
  ...async('CREATE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('DELETE_ALGORITHM_OUTPUT_VARIABLE'),
  ...async('FETCH_ALGORITHM_IMPLEMENTATION'),
  ...async('CREATE_ALGORITHM_IMPLEMENTATION'),
  ...async('UPDATE_ALGORITHM_IMPLEMENTATION'),
  ...async('DELETE_ALGORITHM_IMPLEMENTATION'),

  ...async('CREATE_ACCESS_INPUT'),
  ...async('UPDATE_ACCESS_INPUT'),
  ...async('DELETE_ACCESS_INPUT'),

  ...async('CREATE_ACCESS_OUTPUT'),
  ...async('UPDATE_ACCESS_OUTPUT'),
  ...async('DELETE_ACCESS_OUTPUT'),

  ...async('CREATE_ACCESS_RELATED'),
  ...async('UPDATE_ACCESS_RELATED'),
  ...async('DELETE_ACCESS_RELATED'),

  ...async('FETCH_ATBD_VERSION_REFERENCES'),
  ...async('CREATE_REFERENCE'),
  ...async('DELETE_REFERENCE'),
  ...async('UPLOAD_FILE'),
  ...async('FETCH_STATIC'),
  ...async('UPLOAD_JSON'),
  ...async('SERIALIZE_DOCUMENT'),
  ...async('CHECK_PDF'),
  ...async('CHECK_HTML')
]);

export default types;
