import React, { Component } from 'react';
import { PropTypes as T } from 'prop-types';
import styled from 'styled-components/macro';

import RemoveButton from '../styles/button/remove';
import FormInput from '../styles/form/input';
import { themeVal } from '../styles/utils/general';

const InlineContainer = styled.span`
  position: relative;
  > * {
    cursor: default;
  }
`;

const MetaContainer = styled.span`
  display: block;
  position: absolute;
  top: -2.6rem;
  z-index: 10;
`;

const StaticMeta = styled.span`
  color: rgba(0, 0, 0, 0.64);
  background: #FFF;
  box-shadow: ${themeVal('boxShadow.input')};
  display: flex;
  height: 2.5rem;
  justify-content: space-between;
  line-height: 1.5rem;
  padding: 0.5rem 0.75rem;
  user-select: none;
  min-width: 16rem;
`;

const MetaInput = styled(FormInput)`
  width: 16rem;
`;

export function InlineMetadata(props) {
  const {
    hasActiveSelection,
    metadata,
    readOnly,
    onRemove,
    onSubmit,
    children
  } = props;
  return (
    <InlineContainer>
      {children}
      {hasActiveSelection && (
        <MetadataEditor
          initialValue={metadata}
          readOnly={readOnly}
          onRemove={onRemove}
          onSubmit={onSubmit}
        />
      )}
    </InlineContainer>
  );
}

InlineMetadata.propTypes = {
  hasActiveSelection: T.bool,
  readOnly: T.bool,
  metadata: T.oneOfType([
    T.string,
    T.number
  ]),
  onRemove: T.func,
  onSubmit: T.func,
  children: T.node
};

class MetadataEditor extends Component {
  constructor(props) {
    super(props);
    const { initialValue } = props;
    this.state = { value: initialValue };
    this.onChange = this.onChange.bind(this);
    this.onRemove = this.onRemove.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
    this.input = React.createRef();
  }

  onChange(e) {
    this.setState({ value: e.currentTarget.value });
  }

  onRemove() {
    const { onRemove } = this.props;
    if (onRemove) {
      onRemove();
    }
  }

  handleKeyPress(e) {
    const { keyCode } = e;
    // enter
    if (keyCode === 13) {
      e.preventDefault();
      const { value } = this.state;
      const { onSubmit } = this.props;
      onSubmit(value);
    }
  }

  renderMetaEditor() {
    const { value } = this.state;
    const { onChange, handleKeyPress } = this;
    return (
      <MetaInput
        type="text"
        id="metadata-editor"
        size="large"
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyPress}
        ref={this.input}
      />
    );
  }

  renderStaticMeta() {
    const { onRemove } = this.props;
    const { value } = this.state;
    return (
      <StaticMeta>
        <span>{value}</span>
        {!!onRemove && (
          <RemoveButton
            variation="base-plain"
            size="small"
            hideText
          >
            Remove
          </RemoveButton>
        )}
      </StaticMeta>
    );
  }

  render() {
    const { readOnly } = this.props;
    return (
      <MetaContainer contentEditable={false}>
        {readOnly ? this.renderStaticMeta() : this.renderMetaEditor()}
      </MetaContainer>
    );
  }
}

MetadataEditor.propTypes = {
  initialValue: T.string,
  readOnly: T.bool,
  onSubmit: T.func,
  onRemove: T.func
};
export default InlineMetadata;
