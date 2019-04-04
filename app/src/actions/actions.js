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

export function createAtbdVersion(atbd_version) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions`,
      method: 'POST',
      body: JSON.stringify(atbd_version),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ATBD_VERSION,
        types.CREATE_ATBD_VERSION_SUCCEEDED,
        types.CREATE_ATBD_VERSION_FAILED
      ]
    }
  };
}

export function updateAtbdVersion(atbd_id, atbd_version, document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&atbd_version=eq.${atbd_version}`,
      method: 'PATCH',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_ATBD_VERSION,
        types.UPDATE_ATBD_VERSION_SUCCEEDED,
        types.UPDATE_ATBD_VERSION_FAILED
      ]
    }
  };
}

export function fetchAtbdVersion(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=*,atbd(*),algorithm_input_variables(*),`
        + `algorithm_output_variables(*)`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_ATBD_VERSION,
        types.FETCH_ATBD_VERSION_SUCCEEDED,
        types.FETCH_ATBD_VERSION_FAILED
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

export function createAlgorithmInputVariable(variable) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_input_variables`,
      method: 'POST',
      body: JSON.stringify(variable),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ALGORITHM_INPUT_VARIABLE,
        types.CREATE_ALGORITHM_INPUT_VARIABLE_SUCCEEDED,
        types.CREATE_ALGORITHM_INPUT_VARIABLE_FAILED
      ]
    }
  };
}

export function createAlgorithmOutputVariable(variable) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_output_variables`,
      method: 'POST',
      body: JSON.stringify(variable),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ALGORITHM_OUTPUT_VARIABLE,
        types.CREATE_ALGORITHM_OUTPUT_VARIABLE_SUCCEEDED,
        types.CREATE_ALGORITHM_OUTPUT_VARIABLE_FAILED
      ]
    }
  };
}

export function deleteAlgorithmInputVariable(id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_input_variables?algorithm_input_variable_id=eq.${id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_ALGORITHM_INPUT_VARIABLE,
        types.DELETE_ALGORITHM_INPUT_VARIABLE_SUCCEEDED,
        types.DELETE_ALGORITHM_INPUT_VARIABLE_FAILED
      ]
    }
  };
}

export function deleteAlgorithmOutputVariable(id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_output_variables?algorithm_output_variable_id=eq.${id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_ALGORITHM_OUTPUT_VARIABLE,
        types.DELETE_ALGORITHM_OUTPUT_VARIABLE_SUCCEEDED,
        types.DELETE_ALGORITHM_OUTPUT_VARIABLE_FAILED
      ]
    }
  };
}

export function deleteAtbdContact(atbd_id, contact_id) {
  return {
    [RSAA]: {
      endpoint:
        `${BASE_URL}/atbd_contacts?atbd_id=eq.${atbd_id}&contact_id=eq.${contact_id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_ATBD_CONTACT,
        types.DELETE_ATBD_CONTACT_SUCCEEDED,
        types.DELETE_ATBD_CONTACT_FAILED
      ]
    }
  };
}
