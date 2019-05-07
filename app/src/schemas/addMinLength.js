export default function addMinLength(schema) {
  const newSchema = Object.assign({}, schema);
  const { properties, required } = schema;
  newSchema.properties = Object.keys(properties)
    .reduce((accumulator, key) => {
      const newProperty = Object.assign({}, properties[key]);
      const { type, format } = newProperty;
      if (type === 'string' && required.includes(key)) {
        newProperty.minLength = 1;
      }

      // Make array types compatible with validator
      if (type === 'string' && format === 'ARRAY') {
        newProperty.type = 'array';
      }
      accumulator[key] = newProperty;
      return accumulator;
    }, {});
  return newSchema;
}
