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
            }]
          },
        ],
      },
      {
        object: 'block',
        type: 'image',
        data: {
          src:
            'https://img.washingtonpost.com/wp-apps/imrs.php?src=https://img.washingtonpost.com/news/speaking-of-science/wp-content/uploads/sites/36/2015/10/as12-49-7278-1024x1024.jpg&w=1484'
        }
      },
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
