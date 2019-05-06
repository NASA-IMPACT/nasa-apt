import actions from '../constants/action_types';

const initialState = {
  atbds: [],
  contacts: [],
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
      return { ...state, contacts: [...payload] };
    }

    case actions.FETCH_ATBD_SUCCESS: {
      const { payload } = action;
      return { ...state, selectedAtbd: { ...payload } };
    }

    case actions.CREATE_CONTACT_SUCCESS: {
      const { payload } = action;
      return { ...state, contacts: [...state.contacts, payload] };
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

    case actions.CREATE_REFERENCE_SUCCESS: {
      const { payload } = action;
      return {
        ...state,
        lastCreatedReference: payload
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

    default: return state;
  }
}
