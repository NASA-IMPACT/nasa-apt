import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import Input, { InputLabelFeedback } from '../src/components/common/Input';

configure({ adapter: new Adapter() });

test('Input', (t) => {
  const props = {
    label: 'label',
    name: 'name',
    error: undefined,
    touched: true
  };
  let wrapper = shallow((<Input {...props} />));
  const noFeedback = wrapper.find(InputLabelFeedback);
  t.notOk(noFeedback.text());

  const error = 'error';
  props.error = error;
  wrapper = shallow((<Input {...props} />));
  const feedback = wrapper.find(InputLabelFeedback);
  t.equal(feedback.text(), error);
  t.end();
});
