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
  if (!doc || !Array.isArray(doc.nodes)) return editorBlankDocument;
  return doc;
}
