import { test, expect } from '@playwright/test';

test.describe('Transactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', 'test@example.com');
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', 'TestPass123');
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    await page.waitForTimeout(2000);
  });

  test('should display send money page', async ({ page }) => {
    await page.goto('/transfer');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'artifacts/screenshots/transactions-send-page.png' });
  });

  test('should display transaction history', async ({ page }) => {
    await page.goto('/transactions');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/transactions-history.png' });
  });
});
