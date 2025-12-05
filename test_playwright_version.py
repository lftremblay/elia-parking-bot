import playwright
print("Playwright imported successfully")

# Test basic browser launch
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.example.com")
        title = page.title()
        print(f"✅ Browser test successful. Page title: {title}")
        browser.close()
except Exception as e:
    print(f"❌ Browser test failed: {e}")
