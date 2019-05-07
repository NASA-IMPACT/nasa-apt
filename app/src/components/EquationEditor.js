import React from 'react';
import propTypes from 'prop-types';
import styled from 'styled-components/macro';
import 'katex/dist/katex.min.css';
import { BlockMath } from 'react-katex';

const EquationBlock = styled.div`
  > * {
    margin-bottom: 1.5rem;
  }
`;

const EquationEditor = (props) => {
  const latexClass = {
    backgroundColor: '#eee',
    textAlign: 'center'
  };
  const { children, node: { text } } = props;
  return (
    <EquationBlock>
      <pre style={latexClass}>
        {children}
      </pre>
      <div contentEditable={false}>
        <BlockMath math={text} />
      </div>
    </EquationBlock>
  );
};

EquationEditor.propTypes = {
  children: propTypes.array.isRequired,
  node: propTypes.object.isRequired
};

export default EquationEditor;
