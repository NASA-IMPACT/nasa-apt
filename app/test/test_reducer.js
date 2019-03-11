import test from 'tape';
import reducer from '../src/reducers/reducer';
import { FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED }
  from '../src/constants/action_types';

test('initialState is a Slatejs immutable value', (t) => {
  const initialState = reducer(undefined, {});
  const { algorithmDescription } = initialState;
  t.equal(algorithmDescription.constructor.name, 'Value');
  t.end();
});

test('FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED parses payload', (t) => {
  const type = 'paragraph';
  const document = {
    nodes: [{
      object: 'block',
      type,
      nodes: []
    }]
  };
  const action = {
    type: FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED,
    payload: [{
      data_model: {
        document
      }
    }]
  };
  const state = reducer(undefined, action);
  const { algorithmDescription } = state;
  t.equal(algorithmDescription.getIn(['document', 'nodes', 0, 'type']), type);
  t.end();
});
