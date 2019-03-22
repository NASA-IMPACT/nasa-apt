import { Value } from 'slate';
import * as actions from '../constants/action_types';

const algorithmDescription = Value.fromJSON({
  document: {
    nodes: [
      {
        object: 'block',
        type: 'paragraph',
        nodes: [
          {
            object: 'text',
            leaves: [
              {
                text: 'A line of text in a paragraph.',
              },
            ],
          },
        ],
      },
    ],
  },
});

const initialState = {
  algorithmDescription,
  atbds: []
};

export default function (state = initialState, action) {
  switch (action.type) {
    case actions.FETCH_ALGORITHM_DESCRIPTION_SUCCEEDED: {
      const { payload } = action;
      const document = Value.fromJSON({
        document: payload[0].scientific_theory.document
      });
      return { algorithmDescription: document };
    }
    case actions.FETCH_ATBDS_SUCCEEDED: {
      const { payload } = action;
      return Object.assign({}, state, { atbds: [...payload] });
    }
    case actions.FETCH_ATBD_SUCCEEDED: {
      const { payload } = action;
      return Object.assign({}, state, { selectedAtbd: payload });
    }
    default: return state;
  }
}
