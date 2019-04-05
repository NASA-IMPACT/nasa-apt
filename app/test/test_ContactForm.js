import React from 'react';
import Adapter from 'enzyme-adapter-react-16';
import { shallow, configure } from 'enzyme';
import test from 'tape';
import sinon from 'sinon';
import { InputSubmit } from '../src/components/common/Input';

const proxyquire = require('proxyquire').noCallThru();

configure({ adapter: new Adapter() });

test('InnerContactForm submit disabled', (t) => {
  const { InnerContactForm } = proxyquire(
    '../src/components/ContactForm',
    {
      '../actions/actions': {
        createContact: () => {}
      }
    }
  );
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
  let submit = wrapper.find(InputSubmit);
  t.ok(submit.props().disabled, 'Submit disabled when there are errors');

  props.errors = {};
  wrapper = shallow((<InnerContactForm {...props} />));
  submit = wrapper.find(InputSubmit);
  t.notOk(submit.props().disabled, 'Submit enabled when there are no errors');
  t.end();
});

test('ContactForm validation', (t) => {
  const transformErrors = sinon.stub().returns({});
  const validateEmail = sinon.stub().returns(false);
  const email = 'Email';
  const { ContactForm } = proxyquire(
    '../src/components/ContactForm',
    {
      '../schemas/transformErrors': transformErrors,
      '../schemas/validateEmail': validateEmail,
      '../actions/actions': {
        createContact: () => {}
      }
    }
  );

  const wrapper = shallow((<ContactForm />));
  const instance = wrapper.instance();
  const errors = instance.validate({ contact_mechanism_type: email });
  t.ok(errors.contact_mechanism_value, 'Adds error when email is invalid');
  t.end();
});
