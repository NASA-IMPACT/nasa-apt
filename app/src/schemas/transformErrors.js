export default function transformErrors(errors) {
  const transformedErrors = errors.reduce((accumulator, error) => {
    const { property, argument, message } = error;
    if (property === 'instance') {
      accumulator[argument] = message;
    } else {
      const propertyName = property.split('.')[1];
      accumulator[propertyName] = message;
    }
    return accumulator;
  }, {});
  return transformedErrors;
}
