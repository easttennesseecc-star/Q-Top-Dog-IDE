import { test, expect } from '@playwright/test';
import { spawn, type ChildProcessWithoutNullStreams } from 'child_process';
import net from 'net';

// Start backend automatically for E2E and tear down after tests.
let serverProc: ChildProcessWithoutNullStreams | null = null;

const waitForPort = (port: number, host = '127.0.0.1', timeout = 15000) => {
  const start = Date.now();
  return new Promise<void>((resolve, reject) => {
    const tryConn = () => {
      const sock = net.createConnection({ port, host }, () => {
        sock.end();
        resolve();
      });
      sock.on('error', () => {
        if (Date.now() - start > timeout) return reject(new Error('timeout waiting for port'));
        setTimeout(tryConn, 250);
      });
    };
    tryConn();
  });
}

test.beforeAll(async () => {
  // detect python in venv for cross-platform and repo-root venv
  const isWin = process.platform === 'win32';
  const path = await import('path')
  const cwd = process.cwd()
  const candidates = [] as string[]
  // frontend-local venv (if any)
  if (isWin) {
    candidates.push(path.join(cwd, '.venv', 'Scripts', 'python.exe'))
    candidates.push(path.join(cwd, '..', '.venv', 'Scripts', 'python.exe'))
  } else {
    candidates.push(path.join(cwd, '.venv', 'bin', 'python'))
    candidates.push(path.join(cwd, '..', '.venv', 'bin', 'python'))
  }
  // fallback to system python
  candidates.push('python')

  // pick first existing python executable
  let pythonExec: string | null = null
  const fs = await import('fs')
  for (const c of candidates) {
    try {
      if (c === 'python') { pythonExec = c; break }
      if (fs.existsSync(c)) { pythonExec = c; break }
    } catch (e) {}
  }

  if (!pythonExec) {
    console.warn('No python executable found for e2e backend spawn; skipping spawn')
  } else {
    // Run uvicorn from the backend directory so imports like `llm_pool` resolve
    const backendDir = path.join(cwd, '..', 'backend')
    const args = ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000']
    try {
      serverProc = (spawn(pythonExec, args, { stdio: 'inherit', shell: false, cwd: backendDir }) as unknown) as ChildProcessWithoutNullStreams
    } catch (e) {
      console.warn('Failed to spawn backend process automatically', e)
    }
  }

  // wait for port 8000 to accept connections
  await waitForPort(8000, '127.0.0.1', 20000)
})

test.afterAll(async () => {
  if (serverProc) {
    try {
      serverProc.kill();
    } catch (e) {
      // ignore
    }
    serverProc = null;
  }
});

test('run build from UI and show logs', async ({ page, baseURL }) => {
  // Navigate to app
  await page.goto('/');

  // Dump page console and network events to the test runner output for debugging
  page.on('console', msg => console.log('[PAGE_CONSOLE]', msg.text()));
  page.on('request', req => console.log('[PAGE_REQUEST]', req.method(), req.url()));
  page.on('response', res => console.log('[PAGE_RESPONSE]', res.status(), res.url()));

  // Click the Build button and wait for the backend /build/run response
  // There is an aria-label on the build button: 'run-build'
  await page.locator('[aria-label="run-build"]').waitFor({ state: 'visible', timeout: 5000 })
  const [runResp] = await Promise.all([
    page.waitForResponse(resp => resp.url().includes('/build/run') && resp.status() === 200, { timeout: 10000 }),
    page.locator('[aria-label="run-build"]').click(),
  ])
  const payload = await runResp.json().catch(() => ({}))
  if (!payload?.build_id) {
    throw new Error('build/run did not return build_id: ' + JSON.stringify(payload))
  }

  // Expect build queue count to appear
  await expect(page.locator('[aria-label="build-queue-count"]')).toBeVisible({ timeout: 10000 });

  // Open build panel if needed (panel auto-opens)
  await expect(page.getByText('Build Queue')).toBeVisible({ timeout: 5000 });

  // Wait for some logs to appear in the first build's LogPanel
  const firstLogLine = page.locator('[data-testid^="log-line-0"]').first();
  await expect(firstLogLine).toBeVisible({ timeout: 15000 });

  // Optionally assert that final status appears (success/failed)
  await expect(page.locator('.text-xs').first()).toBeVisible();
});
