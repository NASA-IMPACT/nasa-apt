import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import Button from '../styles/atoms/button';
import ButtonGroup from '../styles/molecules/button-group';

const TextContainer = styled.div`
  position: relative;
`;

const ActionsContainer = styled.div`
  position: absolute;
  top: -2.4rem;
`;

const buttonConfig = [{
  display: <strong>B</strong>,
  mark: 'bold'
}, {
  display: <em>i</em>,
  mark: 'italic'
}, {
  display: <u>u</u>,
  mark: 'underline'
}, {
  display: <s>S</s>,
  mark: 'strikethrough'
}];

const baseVariation = 'base-raised-light';
const activeVariation = 'base-raised-semidark';

export function FormattableText(props) {
  const {
    attributes,
    activeMarks,
    hasSelection,
    isFocused,
    children,
    toggleMark
  } = props;
  return (
    <TextContainer>
      {hasSelection && isFocused && (
        <ActionsContainer>
          <ButtonGroup orientation="horizontal">
            {buttonConfig.map(config => (
              <Button
                key={config.mark}
                onClick={() => toggleMark(config.mark)}
                variation={activeMarks.indexOf(config.mark) >= 0 ? activeVariation
                  : baseVariation}
              >
                {config.display}
              </Button>
            ))}
          </ButtonGroup>
        </ActionsContainer>
      )}
      <p {...attributes}>{children}</p>
    </TextContainer>
  );
}

FormattableText.propTypes = {
  attributes: PropTypes.object.isRequired,
  activeMarks: PropTypes.array.isRequired,
  hasSelection: PropTypes.bool,
  isFocused: PropTypes.bool,
  children: PropTypes.node.isRequired,
  toggleMark: PropTypes.func.isRequired
};

export default FormattableText;
