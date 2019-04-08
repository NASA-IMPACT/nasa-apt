import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import sinon from 'sinon';
import { Value } from 'slate';
import { Toolbar } from '../src/components/Toolbars';

configure({ adapter: new Adapter() });

const proxyquire = require('proxyquire').noCallThru();

test('FreeEditor tool selection', (t) => {
  const save = sinon.spy();
  const value = Value.fromJSON({});
  const { FreeEditor } = proxyquire(
    '../src/components/FreeEditor',
    {
      './EquationEditor': () => (<div />)
    }
  );
  const wrapper = shallow(
    <FreeEditor
      save={save}
      value={value}
      className=""
    />
  );
  const equation = 'equation';
  const EquationButton = wrapper.find(Toolbar).shallow()
    .findWhere(n => n.props().id === equation).first();
  EquationButton.simulate('click');
  t.equal(wrapper.state().activeTool, equation);

  const paragraph = 'paragraph';
  const ParagraphButton = wrapper.find(Toolbar).shallow()
    .findWhere(n => n.props().id === paragraph).first();
  ParagraphButton.simulate('click');
  t.equal(wrapper.state().activeTool, paragraph);

  const table = 'table';
  const TableButton = wrapper.find(Toolbar).shallow()
    .findWhere(n => n.props().id === table).first();
  TableButton.simulate('click');
  t.equal(wrapper.state().activeTool, table);

  TableButton.simulate('click');
  t.notOk(wrapper.state().activeTool,
    'Click active tool a second time disables it');
  t.end();
});
