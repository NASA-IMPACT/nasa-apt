import test from 'tape';
import reducer from '../src/reducers/reducer';
import actions from '../src/constants/action_types';

test('initialState has empty atbds and contacts', (t) => {
  const state = reducer(undefined, {});
  t.equal(state.atbds.length, 0);
  t.equal(state.contacts.length, 0);
  t.end();
});

test('FETCH_ATBD_VERSION_SUCCESS', (t) => {
  const payload = {
    atbd_id: 1,
    title: 'Title'
  };
  const state = reducer(undefined, {
    type: actions.FETCH_ATBD_VERSION_SUCCESS,
    payload
  });
  t.notOk(state.atbdVersion === payload,
    'Does not reference payload object for immutability');
  t.equal(state.atbdVersion.atbd_id, payload.atbd_id);
  t.end();
});

test('FETCH_ATBDS_SUCCESS', (t) => {
  const payload = [1, 2, 3, 3];
  const state = reducer(undefined, {
    type: actions.FETCH_ATBDS_SUCCESS,
    payload
  });
  t.notOk(state.atbds === payload,
    'Does not reference payload object for immutability');
  t.deepEqual(state.atbds, payload);
  t.end();
});

test('FETCH_CONTACTS_SUCCESS', (t) => {
  const payload = [1, 2, 3, 3];
  const state = reducer(undefined, {
    type: actions.FETCH_CONTACTS_SUCCESS,
    payload
  });
  t.notOk(state.contacts === payload,
    'Does not reference payload object for immutability');
  t.ok(state.contacts.every(t => !!t.id));
  t.end();
});

test('FETCH_ATBD_SUCCESS', (t) => {
  const payload = {
    atbd_id: 1
  };
  const state = reducer(undefined, {
    type: actions.FETCH_ATBD_SUCCESS,
    payload
  });

  t.notOk(state.selectedAtbd === payload,
    'Does not reference payload object for immutability');
  t.equal(state.selectedAtbd.atbd_id, payload.atbd_id);
  t.end();
});


test('CREATE_ATBD_CONTACT_SUCCESS', (t) => {
  const payload = {
    contact_id: 2
  };

  const previousState = {
    selectedAtbd: {
      contacts: [{
        contact_id: 1
      }]
    },
    contacts: [{
      contact_id: 2
    }]
  };

  // Assumes that list of existing contacts is already in state.
  const state = reducer(previousState, {
    type: actions.CREATE_ATBD_CONTACT_SUCCESS,
    payload
  });
  t.notOk(state.selectedAtbd === previousState.selectedAtbd,
    'Does not mutate for immutability');
  t.notOk(state.selectedAtbd.contacts === previousState.selectedAtbd.contacts,
    'Does not mutate nested array property for immutability');
  t.equal(state.selectedAtbd.contacts.length, 2,
    'Adds new contact association to selectedAtbd contacts');
  t.end();
});

test('CREATE_ALGORITHM_INPUT_VARIABLE_SUCCESS', (t) => {
  const payload = {
    algorithm_input_variable_id: 2
  };

  const previousState = {
    atbdVersion: {
      algorithm_input_variables: [{
        algorithm_input_variable_id: 1
      }]
    }
  };

  const state = reducer(previousState, {
    type: actions.CREATE_ALGORITHM_INPUT_VARIABLE_SUCCESS,
    payload
  });

  t.notOk(state.atbdVersion === previousState.atbdVersion,
    'Does not mutate for immutability');
  t.notOk(state.atbdVersion.algorithm_input_variables
    === previousState.atbdVersion.algorithm_input_variables,
  'Does not mutate nested array property for immutability');
  t.equal(state.atbdVersion.algorithm_input_variables.length, 2,
    'Adds new algorithm input variable to atbdVersion');
  t.end();
});

test('DELETE_ALGORITHM_INPUT_VARIABLE_SUCCESS', (t) => {
  const payload = {
    algorithm_input_variable_id: 1
  };

  const previousState = {
    atbdVersion: {
      algorithm_input_variables: [{
        algorithm_input_variable_id: 1
      }]
    }
  };

  const state = reducer(previousState, {
    type: actions.DELETE_ALGORITHM_INPUT_VARIABLE_SUCCESS,
    payload
  });

  t.notOk(state.atbdVersion === previousState.atbdVersion,
    'Does not mutate for immutability');
  t.notOk(state.atbdVersion.algorithm_input_variables
    === previousState.atbdVersion.algorithm_input_variables,
  'Does not mutate nested array property for immutability');
  t.equal(state.atbdVersion.algorithm_input_variables.length, 0,
    'Removes correct algorithm input variable from atbdVersion');
  t.end();
});

test('DELETE_ATBD_CONTACT_SUCCESS', (t) => {
  const payload = {
    contact_id: 1
  };

  const previousState = {
    selectedAtbd: {
      contacts: [{
        contact_id: 1
      }]
    }
  };

  const state = reducer(previousState, {
    type: actions.DELETE_ATBD_CONTACT_SUCCESS,
    payload
  });

  t.notOk(state.selectedAtbd === previousState.selectedAtbd,
    'Does not mutate for immutability');
  t.notOk(state.selectedAtbd.contacts === previousState.selectedAtbd.contacts,
    'Does not mutate nested array property for immutability');
  t.equal(state.selectedAtbd.contacts.length, 0,
    'Removes correct contact from selectedAtbd');
  t.end();
});

test('CREATE_ATBD_SUCCESS', (t) => {
  const payload = {
    created_atbd: {
      atbd_id: 1
    },
    created_version: {
      atbd_id: 1,
      atbd_version: 1
    }
  };

  const previousState = {
    atbds: [{
      atbd_id: 0
    }]
  };

  const state = reducer(previousState, {
    type: actions.CREATE_ATBD_SUCCESS,
    payload
  });

  t.notOk(state.atbds === previousState.atbds,
    'Does not mutate for immutability');
  t.equal(state.atbds.length, 2,
    'Adds newly created atbd to list');
  t.equal(state.atbds[1].contacts.length, 0,
    'Adds empty contacts property to created atbd in list');
  t.equal(state.atbds[1].atbd_versions[0].atbd_version, 1,
    'Adds created version to created atbd in list');
  t.end();
});
