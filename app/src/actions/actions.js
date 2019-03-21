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

export function fetchAlgorithmDescription(id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${id}&atbd_version=eq.${id}&select=scientific_theory`,
      method: 'GET',
      types: [
        types.FETCH_ALGORITHM_DESCRIPTION,
        types.FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED,
        types.FETCH_ALGORITHM_DESCRIPTION_FAILED
      ]
    }
  };
}
