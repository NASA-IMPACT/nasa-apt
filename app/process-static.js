#!/usr/bin/env node

const path = require('path');
const fs = require('fs');
const yaml = require('js-yaml');

let out = {};
const static = path.join(__dirname, 'static');
fs.readdirSync(static)
  .filter(f => {
    const extension = path.extname(f);
    return extension === '.yml' || extension === '.yaml'
  }).forEach(f => {
    try {
      var content = yaml.safeLoad(fs.readFileSync(path.join(static, f), 'utf8'));
    } catch (e) {
      console.log(e);
      console.log(`Could not process ${f}, skipping`);
      return;
    }
    const key = path.parse(f).name;
    out[key] = content;
  });

fs.writeFileSync(path.join(__dirname, 'public/static.json'), JSON.stringify(out));
