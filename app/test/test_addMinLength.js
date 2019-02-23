import test from 'tape';
import addMinLength from '../src/schemas/addMinLength';

test('addMinLength only adds field to required properties', (t) => {
  const schema = {
    required: [
      'first_name',
      'last_name'
    ],
    properties: {
      first_name: {
        type: 'string',
      },
      middle_name: {
        type: 'string'
      },
      last_name: {
        type: 'string'
      }
    }
  };
  const actual = addMinLength(schema);
  t.equal(actual.properties.first_name.minLength, 1);
  t.notOk(actual.properties.middle_name.minLength);
  t.end();
});
