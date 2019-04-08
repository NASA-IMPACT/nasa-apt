import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import { EditorTable } from '../src/components/EditorTable';

configure({ adapter: new Adapter() });

test('EditorTable table header option', (t) => {
  let headless = false;
  const props = {
    remove: () => true,
    insertRow: () => true,
    removeRow: () => true,
    insertColumn: () => true,
    removeColumn: () => true,
    node: {
      get: () => ({ get: () => headless })
    },
    children: ['a', 'b', 'c'],
    attributes: {}
  };
  const wrapper = shallow(<EditorTable {...props} />);

  t.equal(wrapper.find('thead').length, 1,
    'Defaults to rendering the first element as a <thead>');

  headless = true;
  wrapper.setProps({ ...props });
  t.equal(wrapper.find('thead').length, 0,
    'Responds to option to toggle thead rendering');

  t.end();
});
