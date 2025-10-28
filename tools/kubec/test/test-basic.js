const { spawnSync } = require('child_process');
const path = require('path');

console.log('Running basic kubec --help test...');
const bin = path.resolve(__dirname, '..', 'bin', 'kubec.js');
const res = spawnSync(process.execPath, [bin, '--help'], { stdio: 'inherit' });
if (res.error) {
  console.error('Test failed to execute kubec:', res.error.message);
  process.exit(2);
}
if (res.status !== 0) {
  console.error('kubec exited with non-zero status:', res.status);
  process.exit(1);
}
console.log('kubec --help exited 0 — test passed');
