import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import { InnerContactForm } from '../src/components/ContactForm';

configure({ adapter: new Adapter() });

test('InnerContactForm submit disabled', (t) => {
  const props = {
    values: {},
    touched: {
      first_name: true
    },
    errors: {
      last_name: 'error'
    },
    handleChange: () => {},
    handleBlur: () => {},
    handleSubmit: () => {}
  };
  let wrapper = shallow((<InnerContactForm {...props} />));
  let submit = wrapper.find('button');
  t.ok(submit.props().disabled, 'Submit disabled when there are errors');

  props.errors = {};
  wrapper = shallow((<InnerContactForm {...props} />));
  submit = wrapper.find('button');
  t.notOk(submit.props().disabled, 'Submit enabled when there are no errors');
  t.end();
});
