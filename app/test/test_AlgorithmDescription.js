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
  const wrapper = shallow(
    <AlgorithmDescription
      save={() => {}}
      createAlgorithmInputVariable={() => {}}
      createAlgorithmOutputVariable={() => {}}
    />
  );
  const editor = wrapper.find(FreeEditor).first();
  t.equal(editor.props().value.getIn(['document', 'nodes']).size, 1,
    'Initializes the FreeEditor with the blankDocument value with no atbd_version');
  t.end();
});
