/**
 * Creates a math function that performs the given operation taking into account
 * only the unit of the first value. Eg: 2rem * 2 = 4rem | 2 * 2rem = 4
 * The resulting function accepts 2 agruments to which the given operation
 * will be applied.
 * This function is ready to work with styled-components so that any function
 * passed as an argument will receive the component props.
 *
 * @example Simple function
 * const add = createMathOperation('+');
 * add(2, 2) // -> 4
 *
 * @example Using with themeVal()
 * const multiply = createMathOperation('*');
 * multiply(themeVal('globalSpacing'), 2) // -> 2rem
 *
 * @param {string} op Math operation to perform. Can be + - * /
 */
const createMathOperation = op => (inputA, inputB) => (...args) => {
  const a = typeof inputA === 'function' ? inputA(...args) : inputA;
  const b = typeof inputB === 'function' ? inputB(...args) : inputB;

  // The final unit is driven by the `a` value.
  const unit = (`${a}`).match(/[0-9]*(?:.[0-9]+)?(.*)/)[1];
  const aVal = parseFloat(a);
  const bVal = parseFloat(b);

  if (op === '+') {
    return `${aVal + bVal}${unit}`;
  } if (op === '-') {
    return `${aVal - bVal}${unit}`;
  } if (op === '/') {
    return `${aVal / bVal}${unit}`;
  } if (op === '*') {
    return `${aVal * bVal}${unit}`;
  }
};

/**
 * Creates a math function to add values. It takes into account
 * only the unit of the first value. Eg: 2rem + 2 = 4rem | 2 + 2rem = 4
 * This function is ready to work with styled-components so that any function
 * passed as an argument will receive the component props.
 *
 * @param {string} a First value
 * @param {string} b Second value
 */
export const add = createMathOperation('+');

/**
 * Creates a math function to subtract values. It takes into account
 * only the unit of the first value. Eg: 4rem - 2 = 2rem | 4 - 2rem = 2
 * This function is ready to work with styled-components so that any function
 * passed as an argument will receive the component props.
 *
 * @param {string} a First value
 * @param {string} b Second value
 */
export const subtract = createMathOperation('-');

/**
 * Creates a math function to divide values. It takes into account
 * only the unit of the first value. Eg: 4rem / 2 = 2rem | 4 / 2rem = 2
 * This function is ready to work with styled-components so that any function
 * passed as an argument will receive the component props.
 *
 * @param {string} a First value
 * @param {string} b Second value
 */
export const divide = createMathOperation('/');

/**
 * Creates a math function to add values. It takes into account
 * only the unit of the first value. Eg: 2rem * 2 = 4rem | 2 * 2rem = 4
 * This function is ready to work with styled-components so that any function
 * passed as an argument will receive the component props.
 *
 * @param {string} a First value
 * @param {string} b Second value
 */
export const multiply = createMathOperation('*');
