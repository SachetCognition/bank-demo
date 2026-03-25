import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  const testUser = {
    name: 'Test User',
    email: `testuser_${Date.now()}@example.com`,
    password: 'TestPass123',
  };

  test('should register a new user', async ({ page }) => {
    await page.goto('/register');
    await page.screenshot({ path: 'artifacts/screenshots/auth-register-page.png' });
    
    await page.fill('input[name="name"], input[placeholder*="name" i]', testUser.name);
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', testUser.email);
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', testUser.password);
    
    await page.screenshot({ path: 'artifacts/screenshots/auth-register-filled.png' });
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Register"), button:has-text("Sign Up")');
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/auth-register-result.png' });
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.screenshot({ path: 'artifacts/screenshots/auth-login-page.png' });
    
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', testUser.email);
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', testUser.password);
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/auth-login-result.png' });
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', 'invalid@example.com');
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', 'wrongpassword');
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'artifacts/screenshots/auth-login-invalid.png' });
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"], input[placeholder*="email" i], input[type="email"]', testUser.email);
    await page.fill('input[name="password"], input[placeholder*="password" i], input[type="password"]', testUser.password);
    const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await submitButton.click();
    await page.waitForTimeout(2000);
    
    // Logout
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout"), button:has-text("Log Out")');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'artifacts/screenshots/auth-logout-result.png' });
  });
});
