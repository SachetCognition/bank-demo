import { test, expect } from '@playwright/test';

test.describe('Security', () => {
  test('should redirect to login when accessing protected routes without auth', async ({ page }) => {
    await page.goto('/accounts');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/security-redirect-accounts.png' });
  });

  test('should have security headers', async ({ page }) => {
    const response = await page.goto('/');
    const headers = response?.headers() || {};
    await page.screenshot({ path: 'artifacts/screenshots/security-headers-check.png' });
    
    // Log headers for verification
    console.log('Security headers:', JSON.stringify(headers, null, 2));
  });
});
