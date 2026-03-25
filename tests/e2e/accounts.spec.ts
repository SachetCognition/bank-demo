import { test, expect } from '@playwright/test';

test.describe('Accounts', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', 'test@example.com');
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', 'TestPass123');
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    await page.waitForTimeout(2000);
  });

  test('should display accounts page', async ({ page }) => {
    await page.goto('/accounts');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/accounts-page.png' });
  });

  test('should create a new account', async ({ page }) => {
    await page.goto('/new-account');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'artifacts/screenshots/accounts-new-page.png' });
    
    // Fill account creation form based on available fields
    const nameField = page.locator('input[name="name"], input[placeholder*="name" i]');
    if (await nameField.isVisible()) {
      await nameField.fill('Test User');
    }
    
    await page.screenshot({ path: 'artifacts/screenshots/accounts-new-filled.png' });
  });

  test('should view account details', async ({ page }) => {
    await page.goto('/accounts');
    await page.waitForTimeout(2000);
    
    const accountLink = page.locator('a, button, [role="button"], tr').first();
    if (await accountLink.isVisible()) {
      await accountLink.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'artifacts/screenshots/accounts-detail.png' });
  });
});
