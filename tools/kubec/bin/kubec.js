#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

function help() {
  console.log(`kubec - tiny kubectl helper\n
Usage:\n  kubec <cmd> [args]\n
Commands:\n  ctx            Show current context and available contexts\n  get <res>      Run 'kubectl get <res>' (pods, svc, nodes, etc.)\n  logs <pod>     Tail logs for a pod\n  apply <file>   kubectl apply -f <file>\n  exec <pod> ... Exec into a pod\n  --help         Show this help\n`);
}

function runKubectl(args) {
  const kubectl = process.env.KUBECTL_PATH || 'kubectl';

  // Determine KUBECONFIG to use for this invocation.
  // Priority: process.env.KUBECONFIG -> user default (~/.kube/config) -> repo sample
  let kubeconfig = process.env.KUBECONFIG;
  if (!kubeconfig) {
    const userHome = process.env.USERPROFILE || process.env.HOME || '';
    const userCfg = path.join(userHome, '.kube', 'config');
    if (userHome && fs.existsSync(userCfg)) {
      kubeconfig = userCfg;
    } else {
      const sample = path.resolve(__dirname, '..', 'sample-kubeconfig.yaml');
      if (fs.existsSync(sample)) {
        // safe fallback to repo-local sample. Warn so the user knows.
        console.warn(`No kubeconfig found at user path; falling back to repo sample kubeconfig: ${sample}`);
        kubeconfig = sample;
      }
    }
  }

  const childEnv = Object.assign({}, process.env);
  if (kubeconfig) childEnv.KUBECONFIG = kubeconfig;

  const res = spawnSync(kubectl, args, { stdio: 'inherit', env: childEnv });
  if (res.error) {
    console.error('Failed to run kubectl:', res.error.message);
    process.exit(1);
  }
  process.exit(res.status);
}

const argv = process.argv.slice(2);
if (argv.length === 0 || argv[0] === '--help' || argv[0] === '-h') {
  help();
  process.exit(0);
}

const cmd = argv[0];
if (cmd === 'ctx') {
  // show current context and contexts list
  runKubectl(['config', 'get-contexts']);
} else if (cmd === 'get') {
  if (!argv[1]) { console.error('Missing resource type for get'); help(); process.exit(1); }
  runKubectl(['get', argv[1], ...argv.slice(2)]);
} else if (cmd === 'logs') {
  if (!argv[1]) { console.error('Missing pod name for logs'); help(); process.exit(1); }
  runKubectl(['logs', '-f', argv[1], ...argv.slice(2)]);
} else if (cmd === 'apply') {
  if (!argv[1]) { console.error('Missing file for apply'); help(); process.exit(1); }
  runKubectl(['apply', '-f', argv[1]]);
} else if (cmd === 'exec') {
  if (!argv[1]) { console.error('Missing pod name for exec'); help(); process.exit(1); }
  runKubectl(['exec', '-it', argv[1], '--', ...argv.slice(2)]);
} else {
  // passthrough to kubectl
  runKubectl(argv);
}
