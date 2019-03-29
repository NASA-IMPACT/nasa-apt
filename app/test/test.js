/* eslint import/no-extraneous-dependencies: 0 */
require('@babel/register')({
  presets: ['react-app']
});

require('./test_addMinLength');
require('./test_Input');
require('./test_ContactForm');
require('./test_FreeEditor');
require('./test_AlgorithmDescription');
//require('./test_reducer');
