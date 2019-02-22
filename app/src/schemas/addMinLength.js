export default function addMinLength(schema) {
  const newSchema = Object.assign({}, schema);
  const { properties } = schema;
  newSchema.properties = Object.keys(properties)
    .reduce((accumulator, key) => {
      const newProperty = Object.assign({}, properties[key]);
      const { type } = newProperty;
      if (type === 'string') {
        newProperty.minLength = 1;
      }
      accumulator[key] = newProperty;
      return accumulator;
    }, {});
  return newSchema;
}
