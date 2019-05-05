import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';

const proxyquire = require('proxyquire').noCallThru();

const FreeEditor = () => (<div />);
const { AlgorithmDescription } = proxyquire(
  '../src/components/AlgorithmDescription',
  {
    '../actions/actions': {},
    './FreeEditor': FreeEditor
  }
);
configure({ adapter: new Adapter() });

test('AlgorithmDescription editor values', (t) => {
  const atbdVersion = {
    atbd: {},
    atbd_id: 0,
    atbd_version: 1
  };
  const wrapper = shallow(
    <AlgorithmDescription
      atbdVersion={atbdVersion}
      save={() => {}}
      createAlgorithmInputVariable={() => {}}
      createAlgorithmOutputVariable={() => {}}
      deleteAlgorithmInputVariable={() => {}}
      deleteAlgorithmOutputVariable={() => {}}
      updateAtbdVersion={() => {}}
      t={{}}
    />
  );
  const editor = wrapper.find(FreeEditor).first();
  t.equal(editor.props().initialValue, undefined,
    'Initializes the FreeEditor without a defined initialValue');

  const loadingWrapper = shallow(
    <AlgorithmDescription
      save={() => {}}
      createAlgorithmInputVariable={() => {}}
      createAlgorithmOutputVariable={() => {}}
      deleteAlgorithmInputVariable={() => {}}
      deleteAlgorithmOutputVariable={() => {}}
      updateAtbdVersion={() => {}}
      t={{}}
    />
  );
  const div = loadingWrapper.find('div').first();
  t.equal(div.text(), 'Loading', 'Returns Loading div when atbdVersion is loading');
  t.end();
});
