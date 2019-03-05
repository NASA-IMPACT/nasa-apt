import isUrl from 'is-url';

export default {
  document: {
    nodes: [
      {
        match: [{ type: 'paragraph' }, { type: 'image' }, { type: 'equation' }],
      },
    ],
  },
  blocks: {
    paragraph: {
      nodes: [
        {
          match: { object: 'text' },
        },
      ],
    },
    equation: {
      nodes: [
        {
          match: { object: 'text' },
        },
      ],
    },
    image: {
      isVoid: true,
      data: {
        src: v => v && isUrl(v),
      },
    },
  },
};
