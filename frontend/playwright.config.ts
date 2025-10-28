import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:1431',
    headless: true,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 5000,
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'pnpm dev',
    cwd: process.cwd(),
    port: 1431,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
