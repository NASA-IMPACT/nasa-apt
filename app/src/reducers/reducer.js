import * as actions from '../constants/action_types';

//const algorithmDescription = Value.fromJSON({
  //document: {
    //nodes: [
      //{
        //object: 'block',
        //type: 'paragraph',
        //nodes: [
          //{
            //object: 'text',
            //leaves: [
              //{
                //text: 'A line of text in a paragraph.',
              //},
            //],
          //},
        //],
      //},
    //],
  //},
//});

const initialState = {
  atbds: [],
  contacts: []
};

export default function (state = initialState, action) {
  switch (action.type) {
    case actions.FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED: {
      const { payload } = action;
      return { ...state, algorithmDescription: payload };
    }
    case actions.FETCH_ATBDS_SUCCEEDED: {
      const { payload } = action;
      return { ...state, atbds: [...payload] };
    }
    case actions.FETCH_CONTACTS_SUCCEEDED: {
      const { payload } = action;
      return { ...state, contacts: [...payload] };
    }
    case actions.FETCH_ATBD_SUCCEEDED: {
      const { payload } = action;
      return { ...state, selectedAtbd: payload };
    }
    case actions.CREATE_CONTACT_SUCCEEDED: {
      const { payload } = action;
      return { ...state, contacts: [...state.contacts, payload] };
    }
    case actions.CREATE_ATBD_CONTACT_SUCCEEDED: {
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
    default: return state;
  }
}
