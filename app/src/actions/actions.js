/* global File, FormData, fetch, DOMParser, Response */
import { RSAA } from 'redux-api-middleware';
import uuid from 'uuid/v1';
import types from '../constants/action_types';

const BASE_URL = process.env.REACT_APP_API_URL;
const s3Uri = process.env.REACT_APP_S3_URI;
const figuresBucket = process.env.REACT_APP_FIGURES_BUCKET;

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
        types.CREATE_CONTACT_SUCCESS,
        types.CREATE_CONTACT_FAIL
      ]
    }
  };
}

export function createContactGroup(contactGroup) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contact_groups`,
      method: 'POST',
      body: JSON.stringify(contactGroup),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_CONTACT_GROUP,
        types.CREATE_CONTACT_GROUP_SUCCESS,
        types.CREATE_CONTACT_GROUP_FAIL
      ]
    }
  };
}

export function updateContact(contact_id, document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contacts?contact_id=eq.${contact_id}`,
      method: 'PATCH',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_CONTACT,
        types.UPDATE_CONTACT_SUCCESS,
        types.UPDATE_CONTACT_FAIL
      ]
    }
  };
}

export function updateContactGroup(contact_group_id, document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contact_groups?contact_group_id=eq.${contact_group_id}`,
      method: 'PATCH',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_CONTACT_GROUP,
        types.UPDATE_CONTACT_GROUP_SUCCESS,
        types.UPDATE_CONTACT_GROUP_FAIL
      ]
    }
  };
}

export function createAtbd() {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/rpc/create_atbd_version`,
      method: 'POST',
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ATBD,
        types.CREATE_ATBD_SUCCESS,
        types.CREATE_ATBD_FAIL
      ]
    }
  };
}

export function updateAtbd(atbd_id, document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbds?atbd_id=eq.${atbd_id}`,
      method: 'PATCH',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_ATBD,
        types.UPDATE_ATBD_SUCCESS,
        types.UPDATE_ATBD_FAIL
      ]
    }
  };
}

export function fetchCitation(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/citations?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=*`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_CITATIONS,
        types.FETCH_CITATIONS_SUCCESS,
        types.FETCH_CITATIONS_FAIL
      ]
    }
  };
}

export function createCitation(document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/citations`,
      method: 'POST',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_CITATION,
        types.CREATE_CITATION_SUCCESS,
        types.CREATE_CITATION_FAIL
      ]
    }
  };
}

export function updateCitation(citation_id, document) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/citations?citation_id=eq.${citation_id}`,
      method: 'PATCH',
      body: JSON.stringify(document),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_CITATION,
        types.UPDATE_CITATION_SUCCESS,
        types.UPDATE_CITATION_FAIL
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
        types.CREATE_ATBD_VERSION_SUCCESS,
        types.CREATE_ATBD_VERSION_FAIL
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
        types.UPDATE_ATBD_VERSION_SUCCESS,
        types.UPDATE_ATBD_VERSION_FAIL
      ]
    }
  };
}

export function fetchAtbdVersion(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=*,atbd(*)`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_ATBD_VERSION,
        types.FETCH_ATBD_VERSION_SUCCESS,
        types.FETCH_ATBD_VERSION_FAIL
      ]
    }
  };
}

export function fetchAtbdVersionVariables(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=*,atbd(*),algorithm_input_variables(*),`
        + `algorithm_output_variables(*)`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_ALGORITHM_VARIABLES,
        types.FETCH_ALGORITHM_VARIABLES_SUCCESS,
        types.FETCH_ALGORITHM_VARIABLES_FAIL
      ]
    }
  };
}

export function fetchAtbds() {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbds?select=*,contacts(*),atbd_versions(atbd_id, atbd_version, status)`,
      method: 'GET',
      types: [
        types.FETCH_ATBDS,
        types.FETCH_ATBDS_SUCCESS,
        types.FETCH_ATBDS_FAIL
      ]
    }
  };
}

export function fetchAtbd(atbd_id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbds?atbd_id=eq.${atbd_id}&select=*,contacts(*),contact_groups(*)`,
      method: 'GET',
      headers: { Accept: 'application/vnd.pgrst.object+json' },
      types: [
        types.FETCH_ATBD,
        types.FETCH_ATBD_SUCCESS,
        types.FETCH_ATBD_FAIL
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
        types.FETCH_CONTACTS_SUCCESS,
        types.FETCH_CONTACTS_FAIL
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
        types.CREATE_ATBD_CONTACT_SUCCESS,
        types.CREATE_ATBD_CONTACT_FAIL
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
        types.DELETE_ATBD_CONTACT_SUCCESS,
        types.DELETE_ATBD_CONTACT_FAIL
      ]
    }
  };
}

export function fetchContactGroups() {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/contact_groups`,
      method: 'GET',
      types: [
        types.FETCH_CONTACT_GROUPS,
        types.FETCH_CONTACT_GROUPS_SUCCESS,
        types.FETCH_CONTACT_GROUPS_FAIL
      ]
    }
  };
}

export function createAtbdContactGroup(atbd_contact_group) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_contact_groups`,
      method: 'POST',
      body: JSON.stringify(atbd_contact_group),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ATBD_CONTACT_GROUP,
        types.CREATE_ATBD_CONTACT_GROUP_SUCCESS,
        types.CREATE_ATBD_CONTACT_GROUP_FAIL
      ]
    }
  };
}

export function deleteAtbdContactGroup(atbd_id, contact_group_id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_contact_groups?atbd_id=eq.${atbd_id}&`
        + `contact_group_id=eq.${contact_group_id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_ATBD_CONTACT_GROUP,
        types.DELETE_ATBD_CONTACT_GROUP_SUCCESS,
        types.DELETE_ATBD_CONTACT_GROUP_FAIL
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
        types.CREATE_ALGORITHM_INPUT_VARIABLE_SUCCESS,
        types.CREATE_ALGORITHM_INPUT_VARIABLE_FAIL
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
        types.CREATE_ALGORITHM_OUTPUT_VARIABLE_SUCCESS,
        types.CREATE_ALGORITHM_OUTPUT_VARIABLE_FAIL
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
        types.DELETE_ALGORITHM_INPUT_VARIABLE_SUCCESS,
        types.DELETE_ALGORITHM_INPUT_VARIABLE_FAIL
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
        types.DELETE_ALGORITHM_OUTPUT_VARIABLE_SUCCESS,
        types.DELETE_ALGORITHM_OUTPUT_VARIABLE_FAIL
      ]
    }
  };
}

export function fetchAlgorithmImplmentations(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/atbd_versions?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}&select=atbd_version,atbd(*),algorithm_implementations(*)`,
      method: 'GET',
      headers: returnObjectHeaders,
      types: [
        types.FETCH_ALGORITHM_IMPLEMENTATION,
        types.FETCH_ALGORITHM_IMPLEMENTATION_SUCCESS,
        types.FETCH_ALGORITHM_IMPLEMENTATION_FAIL
      ]
    }
  };
}

export function createAlgorithmImplementation(implementation) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_implementations`,
      method: 'POST',
      body: JSON.stringify(implementation),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_ALGORITHM_IMPLEMENTATION,
        types.CREATE_ALGORITHM_IMPLEMENTATION_SUCCESS,
        types.CREATE_ALGORITHM_IMPLEMENTATION_FAIL
      ]
    }
  };
}

export function updateAlgorithmImplementation(id, implementation) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_implementations`
        + `?algorithm_implementation_id=eq.${id}`,
      method: 'PATCH',
      body: JSON.stringify(implementation),
      headers: returnObjectHeaders,
      types: [
        types.UPDATE_ALGORITHM_IMPLEMENTATION,
        types.UPDATE_ALGORITHM_IMPLEMENTATION_SUCCESS,
        types.UPDATE_ALGORITHM_IMPLEMENTATION_FAIL
      ]
    }
  };
}

export function deleteAlgorithmImplementation(id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/algorithm_implementations`
        + `?algorithm_implementation_id=eq.${id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_ALGORITHM_IMPLEMENTATION,
        types.DELETE_ALGORITHM_IMPLEMENTATION_SUCCESS,
        types.DELETE_ALGORITHM_IMPLEMENTATION_FAIL
      ]
    }
  };
}

export function fetchAtbdVersionReferences(versionObject) {
  const { atbd_id, atbd_version } = versionObject;
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/publication_references?atbd_id=eq.${atbd_id}&`
        + `atbd_version=eq.${atbd_version}`,
      method: 'GET',
      types: [
        types.FETCH_ATBD_VERSION_REFERENCES,
        types.FETCH_ATBD_VERSION_REFERENCES_SUCCESS,
        types.FETCH_ATBD_VERSION_REFERENCES_FAIL
      ]
    }
  };
}

export function createReference(reference) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/publication_references`,
      method: 'POST',
      body: JSON.stringify(reference),
      headers: returnObjectHeaders,
      types: [
        types.CREATE_REFERENCE,
        types.CREATE_REFERENCE_SUCCESS,
        types.CREATE_REFERENCE_FAIL
      ]
    }
  };
}

export function deleteReference(id) {
  return {
    [RSAA]: {
      endpoint: `${BASE_URL}/publication_references`
        + `?publication_reference_id=eq.${id}`,
      method: 'DELETE',
      headers: returnObjectHeaders,
      types: [
        types.DELETE_REFERENCE,
        types.DELETE_REFERENCE_SUCCESS,
        types.DELETE_REFERENCE_FAIL
      ]
    }
  };
}

export function uploadFile(file) {
  const id = uuid();
  const extension = file.name.split('.').pop();
  const keyedFileName = `${id}.${extension}`;
  const keyedFile = new File([file], keyedFileName, { type: file.type });
  const data = new FormData();
  data.append('success_action_status', '201');
  data.append('Content-Type', keyedFile.type);
  data.append('key', keyedFile.name);
  data.append('file', keyedFile);
  return {
    [RSAA]: {
      endpoint: `http://${s3Uri}/${figuresBucket}`,
      method: 'POST',
      fetch: async (...args) => {
        let location;
        const res = await fetch(...args);
        // Localstack doesn't support key return yet.
        if (res.status === 200) {
          location = `http://${s3Uri}/${figuresBucket}/${keyedFile.name}`;
        } else {
          const text = await res.text();
          const xml = new DOMParser().parseFromString(text, 'application/xml');
          location = xml.getElementsByTagName('Location')[0].textContent;
        }
        return new Response(
          JSON.stringify({
            location
          }),
          {
            status: res.status,
            headers: {
              'Content-Type': 'application/json'
            }
          }
        );
      },
      headers: {
        'Content-Length': keyedFile.size
      },
      body: data,
      types: [
        types.UPLOAD_FILE,
        types.UPLOAD_FILE_SUCCESS,
        types.UPLOAD_FILE_FAIL
      ],
    },
  };
}

export function fetchStatic() {
  return {
    [RSAA]: {
      endpoint: `${process.env.PUBLIC_URL}/static.json`,
      method: 'GET',
      types: [
        types.FETCH_STATIC,
        types.FETCH_STATIC_SUCCESS,
        types.FETCH_STATIC_FAIL
      ]
    }
  };
}
