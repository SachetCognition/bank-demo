import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [['html', { outputFolder: '../../artifacts/e2e-report' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'on',
    video: 'on',
    trace: 'on-first-retry',
  },
  outputDir: '../../artifacts/',
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
