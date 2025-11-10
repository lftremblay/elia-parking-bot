#!/usr/bin/env python3
"""
Quick Playwright test to ensure browser automation works locally
"""

from playwright.sync_api import sync_playwright

def test_playwright():
    """Test Playwright browser functionality"""
    print("🎭 Testing Playwright browser automation...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Test basic navigation
            page.goto("https://example.com")
            title = page.title()
            
            print(f"✅ Page title: {title}")
            print("✅ Playwright working correctly!")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_playwright()
    exit(0 if success else 1)
