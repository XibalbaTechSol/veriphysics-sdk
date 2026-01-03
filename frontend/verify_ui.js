const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    console.log("Starting UI Verification...");

    // Launch browser
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Setup paths
    const screenshotDir = path.join(__dirname, '../screenshots');
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir);
    }

    const timestamp = Date.now();
    const email = `test_user_${timestamp}@example.com`;
    const password = 'SecretPassword123!';

    try {
        // 1. Go to Register
        console.log("Navigating to Register...");
        await page.goto('http://localhost:3000/register');
        await page.waitForSelector('form'); // Wait for hydration
        await page.screenshot({ path: path.join(screenshotDir, '1-register-page.png') });

        // 2. Fill Register
        console.log(`Registering user: ${email}`);
        await page.fill('input[type="email"]', email);
        await page.fill('input[type="password"]', password);
        await page.click('button[type="submit"]');

        // 3. Wait for Redirect to Login
        await page.waitForURL('**/login');
        console.log("Redirected to Login.");
        await page.screenshot({ path: path.join(screenshotDir, '2-login-page.png') });

        // 4. Login
        console.log("Logging in...");
        await page.fill('input[type="email"]', email);
        await page.fill('input[type="password"]', password);
        await page.click('button[type="submit"]');

        // 5. Wait for Dashboard
        await page.waitForURL('**/dashboard');
        console.log("Login Successful. On Dashboard.");

        // Wait for Loading to finish
        try {
            await page.waitForSelector('text=Loading...', { state: 'detached', timeout: 5000 });
        } catch (e) { }

        await page.waitForSelector('h1:has-text("VeriPhysics")');
        await page.screenshot({ path: path.join(screenshotDir, '3-dashboard-initial.png') });

        // 6. Create API Key
        console.log("Creating API Key...");
        // Look for the "Create Key" button. It has a Plus icon or text.
        // The text is "Create Key"
        await page.click('button:has-text("Create Key")');

        // Wait for table to populate (it will reload data)
        await page.waitForTimeout(1000); // Simple wait for fetch refresh
        await page.screenshot({ path: path.join(screenshotDir, '4-dashboard-with-key.png') });

        console.log("Verification Complete. Screenshots saved to /screenshots");

    } catch (error) {
        console.error("Verification Failed:", error);
        await page.screenshot({ path: path.join(screenshotDir, 'error-state.png') });
    } finally {
        await browser.close();
    }
})();
