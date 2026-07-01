import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto('http://localhost:3000', wait_until='networkidle', timeout=15000)
    page.wait_for_timeout(2000)
    page.screenshot(path='D:/gaokao-system/screenshot-home.png', full_page=False)
    print("Home page screenshot saved")

    page.goto('http://localhost:3000/recommend', wait_until='networkidle', timeout=15000)
    page.wait_for_timeout(2000)
    page.screenshot(path='D:/gaokao-system/screenshot-recommend.png', full_page=False)
    print("Recommend page screenshot saved")

    page.goto('http://localhost:3000/trends', wait_until='networkidle', timeout=15000)
    page.wait_for_timeout(2000)
    page.screenshot(path='D:/gaokao-system/screenshot-trends.png', full_page=False)
    print("Trends page screenshot saved")

    browser.close()
