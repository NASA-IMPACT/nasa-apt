import actions from '../constants/action_types';

const initialState = {
  atbds: [],
  contacts: [],
  uploadedFile: undefined,
  atbdVersion: undefined,
  selectedAtbd: undefined,
  performanceAssessment: {
    methods: undefined,
    uncertainties: undefined,
    errors: undefined
  }
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
      const { payload } = action;
      return {
        ...state,
        uploadedFile: payload
      };
    }

    case actions.FETCH_ATBD_VERSION_PERFORMANCE_ASSESSMENT_SUCCESS: {
      const { payload } = action;
      const {
        performance_assessment_validation_methods: methods,
        performance_assessment_validation_uncertainties: uncertainties,
        performance_assessment_validation_errors: errors,
        atbd,
        atbd_id,
        atbd_version
      } = payload;
      return {
        ...state,

        // The performance assessment validation tables are
        // many-to-one with the ATBD versions table; however,
        // in our editing UI it doesn't make sense to display a
        // rich editor for each method, uncertainty, or error.
        //
        // Instead, users have multiple formatting options to
        // write this data as tables, lists, etc. within a single
        // rich editor form.
        performanceAssessment: {
          methods: methods[0],
          uncertainties: uncertainties[0],
          errors: errors[0]
        },
        atbdVersion: {
          atbd,
          atbd_id,
          atbd_version
        }
      };
    }

    default: return state;
  }
}
