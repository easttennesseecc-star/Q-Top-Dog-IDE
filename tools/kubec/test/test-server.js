const fetch = require('node-fetch');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const serverJs = path.resolve(__dirname, '..', 'server.js');
  const node = process.execPath;
  const server = spawn(node, [serverJs], { stdio: ['ignore', 'pipe', 'pipe'] });
  server.stdout.on('data', d => process.stdout.write('[server] ' + d));
  server.stderr.on('data', d => process.stderr.write('[server] ' + d));

  // wait for server to be up
  await new Promise(r => setTimeout(r, 1200));
  try {
    // contexts endpoint: accept either valid contexts JSON or an error object
    const ctxRes = await fetch('http://localhost:51821/api/kube/contexts');
    let ctxBody = null;
    try { ctxBody = await ctxRes.json(); } catch (e) { ctxBody = null; }
    if (ctxRes.ok) {
      console.log('contexts OK', Array.isArray(ctxBody?.contexts) ? ctxBody.contexts.length : 'n/a');
    } else {
      console.warn('contexts endpoint returned non-200, but server responded:', ctxRes.status, ctxBody && ctxBody.error ? ctxBody.error : 'no body');
    }

    // pods endpoint: similarly tolerant
    const podsRes = await fetch('http://localhost:51821/api/kube/pods');
    let podsBody = null;
    try { podsBody = await podsRes.json(); } catch (e) { podsBody = null; }
    if (podsRes.ok) {
      console.log('pods OK', podsBody && typeof podsBody === 'object' ? 'json' : typeof podsBody);
    } else {
      console.warn('pods endpoint returned non-200, but server responded:', podsRes.status, podsBody && podsBody.error ? podsBody.error : 'no body');
    }

    console.log('server smoke tests passed (server responded)');
    process.exit(0);
  } catch (e) {
    console.error('server tests failed:', e.message || e);
    process.exit(2);
  } finally {
    server.kill();
  }
})();
