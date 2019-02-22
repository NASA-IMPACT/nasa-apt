import * as types from '../constants/action_types';

export function createContact(contact) {
  return {
    type: types.CALL_API,
    payload: {
      endpoint: 'contacts',
      authenticated: false,
      types: {
        requestType: types.CREATE_CONTACT,
        successType: types.CREATE_CONTACT_SUCCEEDED,
        errorType: types.CREATE_CONTACT_FAILED
      },
      method: 'POST',
      json: contact
    }
  };
}
