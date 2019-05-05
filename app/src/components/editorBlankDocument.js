import { get } from 'object-path';

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

// Checks if a document is likely to be the default blank document.
// This is not a catch-all check for blank-ness in every sense,
// just a best guess that the user hasn't touched the document at all.
export function isBlankDocument(doc) {
  if (get(doc, 'document.nodes.length') === 1
    && get(doc, 'document.nodes.0.type') === 'paragraph'
    && (get(doc, 'document.nodes.0.nodes.length') === 0
      || get(doc, 'document.nodes.0.nodes.0.leaves.0.text') === '')
  ) {
    return true;
  }
  return false;
}
