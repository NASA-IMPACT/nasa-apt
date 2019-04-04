import { Block, Text } from 'slate';

// Make sure the document always ends in an empty paragraph block,
// except when the last node in a document is already a paragraph block.
// Simplified and modified from below, a plugin which doesn't seem to work anymore.
// https://github.com/GitbookIO/slate-trailing-block/blob/master/lib/index.js
export default function TrailingBlock() {
  return {
    normalizeNode: (node) => {
      if (node.object !== 'document') {
        return undefined;
      }

      const lastNode = node.nodes.last();

      // Don't insert another paragraph if the last node in the document
      // is already a paragraph.
      if (lastNode && lastNode.type === 'paragraph') {
        return undefined;
      }

      const lastIndex = node.nodes.count();
      const block = Block.create({
        type: 'paragraph',
        nodes: [Text.create()]
      });
      return change => change.insertNodeByKey(node.key, lastIndex, block);
    }
  };
}
