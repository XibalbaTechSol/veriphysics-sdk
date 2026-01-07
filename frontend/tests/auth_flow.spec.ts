import { test, expect } from '@playwright/test';

test('auth and dashboard flow', async ({ page }) => {
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', exception => console.log(`PAGE EXCEPTION: ${exception}`));

  // 1. Go to homepage (should redirect to login)
  await page.goto('http://localhost:3000');
  await expect(page).toHaveURL('http://localhost:3000/login');

  // 2. Register a new user
  await page.click('text=Create an account');
  await expect(page).toHaveURL('http://localhost:3000/register');

  const email = `testuser_${Date.now()}@example.com`;
  const password = 'password123';

  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);

  // Verify inputs are filled
  await expect(page.locator('input[type="email"]')).toHaveValue(email);
  await expect(page.locator('input[type="password"]')).toHaveValue(password);

  // Wait for request and response
  const responsePromise = page.waitForResponse(response => response.url().includes('/register') && response.request().method() === 'POST');
  await page.click('button[type="submit"]');
  const response = await responsePromise;

  expect(response.status()).toBe(200);

  // Should redirect to login
  await expect(page).toHaveURL('http://localhost:3000/login');

  // 3. Login
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);

  const loginResponsePromise = page.waitForResponse(response => response.url().includes('/token') && response.request().method() === 'POST');
  await page.click('button[type="submit"]');
  const loginResponse = await loginResponsePromise;
  expect(loginResponse.status()).toBe(200);

  // Should redirect to dashboard
  await expect(page).toHaveURL('http://localhost:3000/dashboard');

  // 4. Check Dashboard Elements
  await expect(page.locator('text=VeriPhysics Dashboard')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'API Keys' })).toBeVisible();

  // 5. Create API Key
  const keyPromise = page.waitForResponse(response => response.url().includes('/api-keys') && response.request().method() === 'POST');
  await page.click('text=Create Key');
  await keyPromise;

  await expect(page.locator('td.font-mono.text-blue-400').first()).toBeVisible();

  // 6. Logout
  await page.click('text=Sign Out');
  await expect(page).toHaveURL('http://localhost:3000/login');
});
