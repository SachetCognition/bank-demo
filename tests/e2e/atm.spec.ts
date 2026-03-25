import { test, expect } from '@playwright/test';

test.describe('ATM Locator', () => {
  test('should display ATM locator page', async ({ page }) => {
    await page.goto('/atm');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/atm-locator-page.png' });
  });

  test('should search for ATMs', async ({ page }) => {
    await page.goto('/atm');
    await page.waitForTimeout(1000);
    
    const searchButton = page.locator('button:has-text("Search"), button:has-text("Find"), button[type="submit"]');
    if (await searchButton.isVisible()) {
      await searchButton.click();
      await page.waitForTimeout(2000);
    }
    await page.screenshot({ path: 'artifacts/screenshots/atm-search-results.png' });
  });
});
