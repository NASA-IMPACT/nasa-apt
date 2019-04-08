/* eslint-disable import/no-extraneous-dependencies */
const { JSDOM } = require('jsdom');

const jsdom = new JSDOM('<!doctype html><html><body></body></html>');
const { window } = jsdom;

function copyProps(src, target) {
  Object.defineProperties(target, {
    ...Object.getOwnPropertyDescriptors(src),
    ...Object.getOwnPropertyDescriptors(target),
  });
}

function setup() {
  global.window = window;
  global.document = window.document;
  global.navigator = {
    userAgent: 'node.js',
  };
  global.requestAnimationFrame = callback => (
    setTimeout(callback, 0)
  );
  global.cancelAnimationFrame = id => (
    clearTimeout(id)
  );
  copyProps(window, global);
}

export default setup;
