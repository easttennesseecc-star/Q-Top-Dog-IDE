#!/usr/bin/env node
// Simple dev server to expose kubectl outputs as JSON for the frontend panel.
// WARNING: intended for local development only.

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.KUBEC_SERVER_PORT || 51821;

function runKubectlJson(args) {
  return new Promise((resolve, reject) => {
    const kubectl = process.env.KUBECTL_PATH || 'kubectl';
    const proc = spawn(kubectl, args);
    let out = '';
    let err = '';
    proc.stdout.on('data', d => out += d.toString());
    proc.stderr.on('data', d => err += d.toString());
    proc.on('close', code => {
      if (code !== 0) return reject(new Error(err || `kubectl exited ${code}`));
      try { resolve(JSON.parse(out)); } catch (ex) { reject(new Error('kubectl output not JSON: ' + ex.message)); }
    });
  });
}

// Determine kubeconfig like kubec does
let kubeconfig = process.env.KUBECONFIG;
if (!kubeconfig) {
  const userHome = process.env.USERPROFILE || process.env.HOME || '';
  const userCfg = path.join(userHome, '.kube', 'config');
  if (userHome && fs.existsSync(userCfg)) kubeconfig = userCfg;
  else {
    const sample = path.resolve(__dirname, 'sample-kubeconfig.yaml');
    if (fs.existsSync(sample)) kubeconfig = sample;
  }
}
if (kubeconfig) process.env.KUBECONFIG = kubeconfig;

app.get('/api/kube/contexts', async (req, res) => {
  try {
    const out = await runKubectlJson(['config', 'view', '--output=json']);
    // return contexts array
    const sampleMode = kubeconfig && kubeconfig.endsWith('sample-kubeconfig.yaml');
    res.json({ contexts: out.contexts || [], currentContext: out['current-context'] || null, kubeconfig, sampleMode });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/kube/pods', async (req, res) => {
  const ns = req.query.namespace || 'default';
  try {
    const pods = await runKubectlJson(['get', 'pods', '-n', ns, '-o', 'json']);
    // include kubeconfig marker so frontend can detect sample-mode
    const out = Object.assign({}, pods, { kubeconfig, sampleMode: kubeconfig && kubeconfig.endsWith('sample-kubeconfig.yaml') });
    res.json(out);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Info endpoint to report kubeconfig used (useful for frontend sample-mode UI)
app.get('/api/kube/info', (req, res) => {
  const sampleMode = kubeconfig && kubeconfig.endsWith('sample-kubeconfig.yaml');
  res.json({ kubeconfig, sampleMode });
});

app.listen(port, () => {
  console.log(`kubec dev server listening on http://localhost:${port}`);
});
