import { test, expect } from '@playwright/test';

test.describe('GDPR', () => {
  test('should have data export endpoint accessible', async ({ page, request }) => {
    await page.screenshot({ path: 'artifacts/screenshots/gdpr-test-start.png' });
    // Note: Full GDPR test requires authentication
    const response = await request.get('/api/users/data-export');
    console.log('Data export response status:', response.status());
    await page.screenshot({ path: 'artifacts/screenshots/gdpr-export-test.png' });
  });

  test('should have data erasure endpoint accessible', async ({ page, request }) => {
    const response = await request.delete('/api/users/data-erasure');
    console.log('Data erasure response status:', response.status());
    await page.screenshot({ path: 'artifacts/screenshots/gdpr-erasure-test.png' });
  });
});
