import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components/macro';
import Button from '../styles/button/button';
import ButtonGroup from '../styles/button/group';
import collecticon from '../styles/collecticons';
import FormInput from '../styles/form/input';

const TextContainer = styled.div`
  position: relative;

  > * {
    margin-bottom: 1.5rem;
  }
`;

const ActionsContainer = styled.div`
  position: absolute;
  top: -2.6rem;
  z-index: 10;
`;

const FixedWidthButton = styled(Button)`
  width: 3rem;
`;

const LinkButton = styled(FixedWidthButton)`
  ::before {
    ${collecticon('link')}
    line-height: 1;
    vertical-align: middle;
  }
`;

const UrlInput = styled(FormInput)`
  width: 20rem;
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
    children,
    hasSelection,
    isFocused,
    activeMarks,
    toggleMark,
    insertLink
  } = props;

  return (
    <TextContainer>
      {hasSelection && isFocused && (
        <FormatOptions
          activeMarks={activeMarks}
          toggleMark={toggleMark}
          insertLink={insertLink}
        />
      )}
      <p {...attributes}>{children}</p>
    </TextContainer>
  );
}

FormattableText.propTypes = {
  attributes: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
  hasSelection: PropTypes.bool,
  isFocused: PropTypes.bool,
  activeMarks: PropTypes.array.isRequired,
  toggleMark: PropTypes.func.isRequired,
  insertLink: PropTypes.func.isRequired
};

// The FormatOptions component is more useful as a separate component,
// as it can make use of `componentDidMount` and `componentWillUnmount`
// lifecycle methods.
export class FormatOptions extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isUrlEditor: false,
      urlValue: ''
    };
    this.toggleUrlEditor = this.toggleUrlEditor.bind(this);
    this.insertLink = this.insertLink.bind(this);
  }

  componentWillUnmount() {
    const { isUrlEditor, urlValue } = this.state;
    if (isUrlEditor && urlValue.length) {
      this.insertLink();
    }
  }

  toggleUrlEditor() {
    return this.setState(state => ({
      isUrlEditor: !state.isUrlEditor
    }));
  }

  insertLink() {
    const { insertLink } = this.props;
    const { urlValue } = this.state;
    insertLink(urlValue);
  }

  renderUrlEditor() {
    const { urlValue } = this.state;
    return (
      <UrlInput
        type="text"
        id="url-editor"
        size="large"
        placeholder="Enter a URL"
        value={urlValue}
        onChange={(e) => {
          this.setState({ urlValue: e.currentTarget.value });
        }}
      />
    );
  }

  renderFormatOptions() {
    const {
      activeMarks,
      toggleMark
    } = this.props;
    const { toggleUrlEditor } = this;
    return (
      <ButtonGroup orientation="horizontal">
        {buttonConfig.map(config => (
          <FixedWidthButton
            key={config.mark}
            onClick={() => toggleMark(config.mark)}
            variation={activeMarks.indexOf(config.mark) >= 0 ? activeVariation
              : baseVariation}
          >
            {config.display}
          </FixedWidthButton>
        ))}
        <LinkButton
          key="link"
          hideText
          variation={baseVariation}
          onClick={toggleUrlEditor}
        >
          Add a link
        </LinkButton>
      </ButtonGroup>
    );
  }

  render() {
    const { isUrlEditor } = this.state;
    return (
      <ActionsContainer contentEditable={false}>
        { isUrlEditor ? this.renderUrlEditor() : this.renderFormatOptions() }
      </ActionsContainer>
    );
  }
}

FormatOptions.propTypes = {
  activeMarks: PropTypes.array.isRequired,
  toggleMark: PropTypes.func.isRequired,
  insertLink: PropTypes.func.isRequired
};

export default FormattableText;
