import isUrl from 'is-url';

export default {
  blocks: {
    paragraph: {
      nodes: [
        {
          match: [{ object: 'text' }, { type: 'link' }, { type: 'reference' }]
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
