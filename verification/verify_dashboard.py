import os
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Login
    page.goto("http://localhost:3000/login")
    page.fill('input[type="email"]', 'tester@example.com')
    page.fill('input[type="password"]', 'password')
    page.click('button[type="submit"]')

    # Wait for dashboard
    expect(page).to_have_url("http://localhost:3000/dashboard")
    expect(page.locator("text=VeriPhysics Dashboard")).to_be_visible()

    # Wait for Job #1 to appear (it should be there already as we ran it via curl)
    expect(page.locator("text=REAL")).to_be_visible()

    # Screenshot - Use relative path or standard artifacts directory
    output_dir = "verification"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    page.screenshot(path=os.path.join(output_dir, "dashboard.png"))

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
