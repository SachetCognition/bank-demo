import { test, expect } from '@playwright/test';

test.describe('Two-Factor Authentication', () => {
  test('should have 2FA setup endpoint', async ({ request }) => {
    const response = await request.post('/api/users/2fa/setup');
    console.log('2FA setup response status:', response.status());
    // Expect 401 since not authenticated
    expect(response.status()).toBe(401);
  });

  test('should have 2FA verify endpoint', async ({ request }) => {
    const response = await request.post('/api/users/2fa/verify', {
      data: { token: '000000' },
    });
    console.log('2FA verify response status:', response.status());
    expect(response.status()).toBe(401);
  });
});
