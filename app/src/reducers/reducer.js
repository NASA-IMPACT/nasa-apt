import actions from '../constants/action_types';

const initialState = {
  atbds: [],
  contacts: [],
  contact_groups: [],
  uploadedFile: undefined,
  atbdVersion: undefined,
  selectedAtbd: undefined,
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

const deleteAtbdChildItem = (schemaKey, state, action) => {
  const idKey = `${schemaKey}_id`;
  const keyPlural = `${schemaKey}s`;

  const { payload } = action;
  const { [idKey]: id } = payload;
  const variables = state.selectedAtbd[keyPlural]
    .filter(variable => (variable[idKey] !== id));
  return {
    ...state,
    selectedAtbd: {
      ...state.selectedAtbd,
      [keyPlural]: variables
    }
  };
};

// Add common metadata to contacts and contact groups,
// to make working with them in combination easier.
const normalizeContact = (contactOrGroup) => {
  const isGroup = contactOrGroup.contact_id ? false : true;
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
  atbd.contacts = Array.isArray(atbd.contacts) ? atbd.contacts.map(normalizeContact) : [];
  atbd.contact_groups = Array.isArray(atbd.contact_groups) ? atbd.contact_groups.map(normalizeContact)
    : [];
  return atbd;
}

export default function (state = initialState, action) {
  switch (action.type) {
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
      return { ...state, selectedAtbd: normalizeSelectedAtbd(payload) }
    }

    case actions.CREATE_CONTACT_SUCCESS: {
      const { payload } = action;
      return { ...state, contacts: [...state.contacts, normalizeContact(payload)] };
    }

    case actions.CREATE_ATBD_CONTACT_SUCCESS: {
      const { payload } = action;
      const addedContact = state.contacts.find(contact => (
        contact.contact_id === payload.contact_id
      ));
      const newState = {
        ...state,
        selectedAtbd: {
          ...state.selectedAtbd,
          contacts: [...state.selectedAtbd.contacts, { ...addedContact }]
        }
      };
      return newState;
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

    case actions.DELETE_ATBD_CONTACT_SUCCESS: {
      const schemaKey = 'contact';
      return deleteAtbdChildItem(schemaKey, state, action);
    }

    case actions.UPLOAD_FILE_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        uploadedFile: payload
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

    case actions.FETCH_STATIC_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        t: payload
      };
    }

    default: return state;
  }
}
