"""
scripts/gen_tv_state.py
=======================
打開 Chrome 讓你手動登入 TradingView，登入完按 Enter，
程式會把 cookies/localStorage 匯出到 tv_state.json。
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_FILE = Path("tv_state.json")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False, channel="chrome")
    context = browser.new_context()        # 乾淨 context
    page = context.new_page()
    page.goto("https://www.tradingview.com/accounts/signin/")

    input("⚠️  請在彈出的瀏覽器手動登入 TradingView，"
          "直到看到圖表頁面，再回到終端機按 Enter...")

    context.storage_state(path=OUT_FILE)   # 寫出 cookies + storage
    print(f"✅ 已將登入狀態存到 {OUT_FILE.resolve()}")

    browser.close()
