import findIndex from 'lodash.findindex';
import actions from '../constants/action_types';

const initialState = {
  atbds: [],
  contacts: [],
  contact_groups: [],
  references: [],
  lastCreatedContact: undefined,
  uploadedFile: undefined,
  atbdVersion: undefined,
  atbdCitation: undefined,
  selectedAtbd: undefined,
  lastCreatedReference: undefined,
  t: undefined
};

const deleteAtbdVersionChildItem = (schemaKey, state, action) => {
  const idKey = `${schemaKey}_id`;
  const keyPlural = `${schemaKey}s`;

  const { payload } = action;
  const { [idKey]: id } = payload;
  const variables = state.atbdVersion[keyPlural]
    .filter(variable => (variable[idKey] !== id));
  return {
    ...state,
    atbdVersion: {
      ...state.atbdVersion,
      [keyPlural]: variables
    }
  };
};

// Add common metadata to contacts and contact groups,
// to make working with them in combination easier.
const normalizeContact = (contactOrGroup) => {
  const isGroup = !contactOrGroup.contact_id;
  const displayName = isGroup ? contactOrGroup.group_name
    : `${contactOrGroup.last_name}, ${contactOrGroup.first_name}`;
  const id = isGroup ? `g${contactOrGroup.contact_group_id}`
    : `c${contactOrGroup.contact_id}`;
  return {
    ...contactOrGroup,
    isGroup,
    displayName,
    id
  };
};

// Normalize contact, contact groups
const normalizeSelectedAtbd = (atbd) => {
  const next = { ...atbd };
  next.contacts = Array.isArray(atbd.contacts) ? atbd.contacts.map(normalizeContact) : [];
  next.contact_groups = Array.isArray(atbd.contact_groups) ? atbd.contact_groups.map(normalizeContact)
    : [];
  return next;
};

const replaceAtIndex = (arr, idProperty, next) => {
  if (!arr || !Array.isArray(arr)) {
    return arr;
  }
  const idx = findIndex(arr, c => c[idProperty] === next[idProperty]);
  if (idx >= 0) {
    const result = arr.slice();
    result[idx] = Object.assign({}, next);
    return result;
  }
  return arr;
};

export default function (state = initialState, action) {
  switch (action.type) {
    case actions.FETCH_ALGORITHM_VARIABLES_SUCCESS:
    case actions.FETCH_ALGORITHM_IMPLEMENTATION_SUCCESS:
    case actions.FETCH_ATBD_VERSION_SUCCESS: {
      const { payload } = action;
      return { ...state, atbdVersion: { ...payload } };
    }

    case actions.FETCH_ATBDS_SUCCESS: {
      const { payload } = action;
      return { ...state, atbds: [...payload] };
    }

    case actions.FETCH_CONTACTS_SUCCESS: {
      const { payload } = action;
      return { ...state, contacts: [...payload.map(normalizeContact)] };
    }

    case actions.FETCH_CONTACT_GROUPS_SUCCESS: {
      const { payload } = action;
      return { ...state, contact_groups: [...payload.map(normalizeContact)] };
    }

    case actions.FETCH_ATBD_SUCCESS: {
      const { payload } = action;
      return { ...state, selectedAtbd: normalizeSelectedAtbd(payload) };
    }

    case actions.CREATE_CONTACT_GROUP_SUCCESS:
    case actions.CREATE_CONTACT_SUCCESS: {
      const next = normalizeContact(action.payload);
      const group = next.isGroup ? 'contact_groups' : 'contacts';
      return {
        ...state,
        [group]: [...state[group], next],
        lastCreatedContact: next
      };
    }

    case actions.CREATE_ATBD_CONTACT_GROUP_SUCCESS:
    case actions.CREATE_ATBD_CONTACT_SUCCESS: {
      const { payload } = action;
      const idProperty = payload.contact_id ? 'contact_id' : 'contact_group_id';
      const group = payload.contact_id ? 'contacts' : 'contact_groups';
      const addedContact = state[group].find(d => (
        d[idProperty] === payload[idProperty]
      ));
      const newState = {
        ...state,
        selectedAtbd: {
          ...state.selectedAtbd,
          [group]: [...state.selectedAtbd[group], { ...addedContact }]
        }
      };
      return newState;
    }

    case actions.DELETE_ATBD_CONTACT_GROUP_SUCCESS:
    case actions.DELETE_ATBD_CONTACT_SUCCESS: {
      const { payload } = action;
      const idProperty = payload.contact_id ? 'contact_id' : 'contact_group_id';
      const group = payload.contact_id ? 'contacts' : 'contact_groups';
      return {
        ...state,
        selectedAtbd: {
          ...state.selectedAtbd,
          [group]: state.selectedAtbd[group].filter(d => d[idProperty] !== payload[idProperty])
        }
      };
    }

    case actions.UPDATE_CONTACT_GROUP_SUCCESS:
    case actions.UPDATE_CONTACT_SUCCESS: {
      const next = normalizeContact(action.payload);
      const group = next.isGroup ? 'contact_groups' : 'contacts';
      const idProperty = next.isGroup ? 'contact_group_id' : 'contact_id';
      return {
        ...state,
        [group]: replaceAtIndex(state[group], idProperty, next),
        selectedAtbd: {
          ...state.selectedAtbd,
          [group]: replaceAtIndex(state.selectedAtbd[group], idProperty, next)
        }
      };
    }

    case actions.CREATE_ALGORITHM_INPUT_VARIABLE_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        atbdVersion: {
          ...state.atbdVersion,
          algorithm_input_variables:
            [...state.atbdVersion.algorithm_input_variables, { ...payload }]
        }
      };
    }

    case actions.CREATE_ALGORITHM_OUTPUT_VARIABLE_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        atbdVersion: {
          ...state.atbdVersion,
          algorithm_output_variables:
            [...state.atbdVersion.algorithm_output_variables, { ...payload }]
        }
      };
    }

    case actions.DELETE_ALGORITHM_INPUT_VARIABLE_SUCCESS: {
      const schemaKey = 'algorithm_input_variable';
      return deleteAtbdVersionChildItem(schemaKey, state, action);
    }

    case actions.DELETE_ALGORITHM_OUTPUT_VARIABLE_SUCCESS: {
      const schemaKey = 'algorithm_output_variable';
      return deleteAtbdVersionChildItem(schemaKey, state, action);
    }

    case actions.UPLOAD_FILE_SUCCESS: {
      const { payload: { location } } = action;
      return {
        ...state,
        uploadedFile: location
      };
    }

    case actions.CREATE_ATBD_SUCCESS: {
      const { payload } = action;
      const { created_atbd, created_version } = payload;
      const newAtbd = {
        ...created_atbd,
        contacts: [],
        contact_groups: [],
        atbd_versions: [{ ...created_version }]
      };
      return { ...state, atbds: [...state.atbds, newAtbd] };
    }

    case actions.CREATE_ALGORITHM_IMPLEMENTATION_SUCCESS: {
      const { payload } = action;
      const next = (state.atbdVersion.algorithm_implementations || [])
        .concat([payload]);
      return {
        ...state,
        atbdVersion: {
          ...state.atbdVersion,
          algorithm_implementations: next
        }
      };
    }

    case actions.DELETE_ALGORITHM_IMPLEMENTATION_SUCCESS: {
      const { payload } = action;
      const id = payload.algorithm_implementation_id;
      const next = state.atbdVersion.algorithm_implementations
        .filter(d => id !== d.algorithm_implementation_id);
      return {
        ...state,
        atbdVersion: {
          ...state.atbdVersion,
          algorithm_implementations: next
        }
      };
    }

    case actions.FETCH_ATBD_VERSION_REFERENCES_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        references: payload
      };
    }

    case actions.CREATE_REFERENCE_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        lastCreatedReference: payload
      };
    }

    case actions.DELETE_REFERENCE_SUCCESS: {
      const { payload } = action;
      const id = payload.publication_reference_id;
      return {
        ...state,
        references: state.references.filter(d => d.publication_reference_id !== id)
      };
    }

    case actions.FETCH_CITATIONS_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        atbdCitation: payload
      };
    }

    case actions.FETCH_STATIC_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        t: payload
      };
    }

    case actions.SERIALIZE_DOCUMENT: {
      const { payload } = action;
      return {
        ...state,
        serializingAtbdVersion: {
          ...payload
        }
      };
    }

    case actions.CHECK_PDF_SUCCESS: {
      const { payload: { location: pdfLocation } } = action;
      return {
        ...state,
        serializingAtbdVersion: {
          ...state.serializingAtbdVersion,
          pdf: pdfLocation
        }
      };
    }
    case actions.CHECK_HTML_SUCCESS: {
      const { payload: { location: html } } = action;
      return {
        ...state,
        serializingAtbdVersion: {
          ...state.serializingAtbdVersion,
          html
        }
      };
    }
    case actions.SERIALIZE_DOCUMENT_FAIL: {
      // Removes the serializingAtbdVersion state property.
      const { serializingAtbdVersion, ...removedSerializingAtbdVersion } = state;
      return removedSerializingAtbdVersion;
    }

    default: return state;
  }
}
