#!/usr/bin/env python3
"""
Check Playwright and try alternative browser setup
"""
import sys
import os

try:
    import playwright
    print(f"✅ Playwright installed: {getattr(playwright, '__version__', 'unknown')}")

    # Try to manually set up browser paths
    from playwright.async_api import async_playwright

    async def check_browsers():
        async with async_playwright() as p:
            try:
                # Try to launch chromium without channel
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                print("✅ Chromium browser available!")
                await browser.close()
                return True
            except Exception as e:
                print(f"❌ Chromium not available: {e}")
                return False

    import asyncio
    result = asyncio.run(check_browsers())
    if result:
        print("🎉 Browser is ready! You can now run the bot.")
        sys.exit(0)  # Exit successfully

    print("❌ Browser setup failed. Trying manual download...")

    # Try to download browser manually with SSL bypass
    import urllib.request
    import zipfile
    import ssl

    try:
        print("📥 Downloading Chromium browser...")
        url = "https://github.com/microsoft/playwright/releases/download/v1.40.0/chromium-1047-win64.zip"

        # Create browsers directory
        browsers_dir = os.path.join(os.path.dirname(playwright.__file__), 'driver', 'browsers')
        os.makedirs(browsers_dir, exist_ok=True)

        zip_path = os.path.join(browsers_dir, 'chromium.zip')

        # Download with SSL bypass
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, context=ssl_context) as response:
            with open(zip_path, 'wb') as f:
                f.write(response.read())

        print("✅ Browser downloaded, extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(browsers_dir)

        print("✅ Browser extracted successfully!")
        print("🎉 Try running the bot now!")

    except Exception as e:
        print(f"❌ Manual download failed: {e}")
        print("💡 You may need to manually download Chromium from:")
        print("   https://github.com/microsoft/playwright/releases/download/v1.40.0/chromium-1047-win64.zip")

except ImportError as e:
    print(f"❌ Playwright not installed: {e}")
    print("💡 Install with: pip install playwright")
    sys.exit(1)
