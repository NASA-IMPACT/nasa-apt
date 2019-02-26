import { RSAA } from 'redux-api-middleware';
import * as types from '../constants/action_types';

const BASE_URL = process.env.REACT_APP_API_URL;

export function createContact(contact) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contacts`,
      method: 'POST',
      body: JSON.stringify(contact),
      headers: { 'Content-Type': 'application/json' },
      types: [
        types.CREATE_CONTACT,
        types.CREATE_CONTACT_SUCCEEDED,
        types.CREATE_CONTACT_FAILED
      ]
    }
  };
}
