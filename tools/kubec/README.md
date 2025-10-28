kubec - tiny kubectl helper

Place this folder under the repository's `tools/` directory. It's a tiny Node.js CLI wrapper that calls `kubectl` with helpful shortcuts.

Usage examples:

# show contexts
node ./bin/kubec.js ctx

# get pods in current namespace
node ./bin/kubec.js get pods

# tail logs
node ./bin/kubec.js logs my-pod-name

# apply manifest
node ./bin/kubec.js apply ./manifests/deploy.yaml

Notes:
- Ensure `kubectl` is installed and on your PATH, or set the KUBECTL_PATH environment variable to the full path.
- You can `npm link` in this folder to make `kubec` available globally for testing.
