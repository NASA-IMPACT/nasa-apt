const editorBlankDocument = {
  document: {
    nodes: [
      {
        object: 'block',
        type: 'paragraph',
        nodes: [
        ],
      },
    ],
  },
};

export default editorBlankDocument;

export function getValidOrBlankDocument(doc) {
  if (!doc || !doc.document) return editorBlankDocument;
  return doc;
}
