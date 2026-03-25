import { test, expect } from '@playwright/test';

test.describe('Loans', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', 'test@example.com');
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', 'TestPass123');
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    await page.waitForTimeout(2000);
  });

  test('should display loan application page', async ({ page }) => {
    await page.goto('/loan');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'artifacts/screenshots/loans-application-page.png' });
  });

  test('should display loan history', async ({ page }) => {
    await page.goto('/loan-history');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/loans-history.png' });
  });
});
