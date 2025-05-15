from __future__ import annotations
import os, logging, sys, traceback
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from core.result_extractor import BacktestResult

load_dotenv()
TV_EMAIL = os.getenv("TV_EMAIL")
TV_PASSWORD = os.getenv("TV_PASSWORD")
PLAYWRIGHT_TIMEOUT = 60_000  # ms
ARTIFACTS = Path("debug_artifacts/minimal")
ARTIFACTS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

def _dump(page, tag: str) -> None:
    """把目前畫面完整 dump 成 html + png。"""
    page.screenshot(path=ARTIFACTS / f"{tag}.png")
    (ARTIFACTS / f"{tag}.html").write_text(page.content(), "utf-8")
# --------------------------------------------------------------------------- #
# Stealth helpers：啟動瀏覽器與建立隱匿 Context
# --------------------------------------------------------------------------- #
from typing import Final
from fake_useragent import UserAgent
from playwright.sync_api import Browser, BrowserContext

DEFAULT_VIEWPORT: Final = {"width": 1920, "height": 1080}

def _launch_stealth_browser(pw) -> Browser:
    """以常見反偵測參數啟動 Chrome／Chromium。"""
    return pw.chromium.launch(
        headless=False,
        channel="chrome",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
            "--disable-infobars",
        ],
    )

def _new_stealth_context(browser: Browser) -> BrowserContext:
    """隨機 UA + 常用標頭 + JS 覆寫，建立新 context。"""
    ua = UserAgent()
    user_agent = ua.random
    extra_headers = {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-CH-UA-Platform": '"Windows"',
    }
    context = browser.new_context(
        viewport=DEFAULT_VIEWPORT,
        user_agent=user_agent,
        locale="en-US",
        timezone_id="Asia/Taipei",
        extra_http_headers=extra_headers,
    )
    context.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.chrome = {runtime: {}};
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """
    )
    return context

def run_backtest(pine_script: str) -> BacktestResult:
    with sync_playwright() as pw:
        browser = _launch_stealth_browser(pw)   # 隨機 UA、--disable-blink-features
        context = _new_stealth_context(browser) # extra headers + navigator 改寫
        page = context.new_page()


        try:
            # Phase 1
            logging.info("P1 → signin")
            page.goto("https://www.tradingview.com/accounts/signin/",
                      timeout=PLAYWRIGHT_TIMEOUT)
            logging.info("P1 URL: %s", page.url)
            _dump(page, "p1_signin")

            # Phase 2
            logging.info("P2 → fill login")
            page.wait_for_selector('input[type="email"]', timeout=PLAYWRIGHT_TIMEOUT)
            page.fill('input[type="email"]', TV_EMAIL)
            page.fill('input[type="password"]', TV_PASSWORD)
            _dump(page, "p2_filled")
            page.click('button[type="submit"]', timeout=PLAYWRIGHT_TIMEOUT)

            # ※ 這行最常 timeout
            page.wait_for_url("**/chart/**", timeout=PLAYWRIGHT_TIMEOUT)
            logging.info("P2 URL after submit: %s", page.url)
            _dump(page, "p2_after_login")

            # Phase 3
            logging.info("P3 → goto chart")
            page.goto("https://www.tradingview.com/chart/", timeout=PLAYWRIGHT_TIMEOUT)
            logging.info("P3 URL: %s", page.url)
            _dump(page, "p3_chart")

            # Phase 4
            logging.info("P4 → open Pine Editor")
            selector = 'button[aria-label="Pine editor"]'
            page.wait_for_selector(selector, timeout=PLAYWRIGHT_TIMEOUT)
            page.click(selector)
            _dump(page, "p4_editor")

        except Exception as exc:
            logging.error("⚠️  偵錯捕獲：%s", exc)
            traceback.print_exc(file=sys.stderr)
        finally:
            browser.close()

    # 先回傳空結果
    return BacktestResult(0, 0, 0, 0, 0, 0)
