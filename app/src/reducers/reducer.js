import { Value } from 'slate';
// Create our initial value...
const test = Value.fromJSON({
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
      {
        object: 'block',
        type: 'equation',
        nodes: [
          {
            object: 'text',
            leaves: [{
              text: '\\int_0^\\infty x^2 dx',
              marks: [
                {
                  type: 'latex'
                }
              ]
            }]
          },
        ],
      }
    ],
  },
});

const initialState = {
  test
};

export default function (state = initialState, action) {
  switch (action.type) {
    default: return state;
  }
}
