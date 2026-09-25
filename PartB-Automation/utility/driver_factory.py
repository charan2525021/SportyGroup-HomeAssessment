"""Chrome WebDriver factory with the flags we use for local + CI runs."""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


def build_chrome_options(headless: bool) -> Options:
    """Chrome flags we use for local and CI runs."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options


def create_chrome_driver(headless: bool = False) -> WebDriver:
    """Fresh Chrome WebDriver, headless if requested."""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=build_chrome_options(headless))
    if not headless:
        driver.maximize_window()
    return driver
