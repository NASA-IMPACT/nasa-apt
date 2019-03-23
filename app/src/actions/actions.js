import { RSAA } from 'redux-api-middleware';
import * as types from '../constants/action_types';

const BASE_URL = process.env.REACT_APP_API_URL;
const returnObjectHeaders = {
  'Content-Type': 'application/json',
  Accept: 'application/vnd.pgrst.object+json',
  Prefer: 'return=representation'
};

export function createContact(contact) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contacts`,
      method: 'POST',
      body: JSON.stringify(contact),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_CONTACT,
        types.CREATE_CONTACT_SUCCEEDED,
        types.CREATE_CONTACT_FAILED
      ]
    }
  };
}

export function createAlgorithmDescription(dataModel) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_descriptions`,
      method: 'POST',
      body: JSON.stringify(dataModel),
      headers: { 'Content-Type': 'application/json' },
      types: [
        types.CREATE_ALGORITHM_DESCRIPTION,
        types.CREATE_ALGORITHM_DESCRIPTION_SUCCEEDED,
        types.CREATE_ALGORITHM_DESCRIPTION_FAILED
      ]
    }
  };
}

export function fetchAlgorithmDescription(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=*,algorithm_input_variables(*),`
        + `algorithm_output_variables(*)`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_ALGORITHM_DESCRIPTION,
        types.FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED,
        types.FETCH_ALGORITHM_DESCRIPTION_FAILED
      ]
    }
  };
}

export function fetchAtbds() {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbds?select=*,contacts(*)`,
      method: 'GET',
      types: [
        types.FETCH_ATBDS,
        types.FETCH_ATBDS_SUCCEEDED,
        types.FETCH_ATBDS_FAILED
      ]
    }
  };
}

export function fetchAtbd(atbd_id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbds?atbd_id=eq.${atbd_id}&select=*,contacts(*)`,
      method: 'GET',
      headers: { Accept: 'application/vnd.pgrst.object+json' },
      types: [
        types.FETCH_ATBD,
        types.FETCH_ATBD_SUCCEEDED,
        types.FETCH_ATBD_FAILED
      ]
    }
  };
}
export function fetchContacts() {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contacts`,
      method: 'GET',
      types: [
        types.FETCH_CONTACTS,
        types.FETCH_CONTACTS_SUCCEEDED,
        types.FETCH_CONTACTS_FAILED
      ]
    }
  };
}
export function createAtbdContact(atbd_contact) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_contacts`,
      method: 'POST',
      body: JSON.stringify(atbd_contact),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ATBD_CONTACT,
        types.CREATE_ATBD_CONTACT_SUCCEEDED,
        types.CREATE_ATBD_CONTACT_FAILED
      ]
    }
  };
}
