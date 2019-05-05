import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import sinon from 'sinon';
import { Value } from 'slate';
import { Toolbar } from '../src/components/Toolbars';

configure({ adapter: new Adapter() });

const proxyquire = require('proxyquire').noCallThru();

test('FreeEditor initial value', (t) => {
  const save = () => true;
  const initialValue = null;
  const { FreeEditor } = proxyquire(
    '../src/components/FreeEditor',
    {
      './EquationEditor': () => (<div />)
    }
  );
  const wrapper = shallow(
    <FreeEditor
      save={save}
      initialValue={initialValue}
    />
  );
  t.equal(wrapper.state().value.getIn(['document', 'nodes']).size, 1,
    'Initializes the editor with a blank document without an initialValue');

  wrapper.setProps({
    initialValue: {
      document: {
        nodes: [{
          object: 'block',
          type: 'paragraph',
          nodes: []
        }, {
          object: 'block',
          type: 'paragraph',
          nodes: []
        }]
      }
    }
  });
  t.equal(wrapper.state().value.getIn(['document', 'nodes']).size, 2,
    'Updates the internal state value when a new inittialValue prop is detected');

  t.end();
});

test('FreeEditor tool selection', (t) => {
  const save = sinon.spy();
  const initialValue = Value.fromJSON({});
  const { FreeEditor } = proxyquire(
    '../src/components/FreeEditor',
    {
      './EquationEditor': () => (<div />)
    }
  );
  const wrapper = shallow(
    <FreeEditor
      save={save}
      initialValue={initialValue}
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
