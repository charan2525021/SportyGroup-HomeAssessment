"""Shared fixtures: config, driver, api client, balance reset, home page."""

from __future__ import annotations

from typing import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from api.betting_api_client import BettingApiClient
from page.home_page import HomePage
from utility.config import CONFIG, Config
from utility.driver_factory import create_chrome_driver


@pytest.fixture(scope="session")
def config() -> Config:
    return CONFIG


@pytest.fixture(scope="session")
def api_client(config: Config) -> Iterator[BettingApiClient]:
    client = BettingApiClient(
        base_url=config.api_base_url,
        user_id=config.user_id,
        timeout=config.api_timeout,
    )
    yield client
    client.close()


@pytest.fixture
def reset_balance(api_client: BettingApiClient) -> None:
    try:
        response = api_client.reset_balance()
        if response.status_code != 200:
            pytest.skip(
                f"reset_balance returned {response.status_code}; environment may not "
                "support balance reset for this user."
            )
    except Exception as exc:
        pytest.skip(f"reset_balance request failed: {exc}")


@pytest.fixture
def driver(config: Config) -> Iterator[WebDriver]:
    drv = create_chrome_driver(headless=config.headless)
    drv.set_page_load_timeout(30)
    try:
        yield drv
    finally:
        drv.quit()


@pytest.fixture
def home_page(
    driver: WebDriver, config: Config, reset_balance: None
) -> HomePage:
    page = HomePage(driver, timeout=config.ui_timeout)
    page.open(base_url=config.base_url, user_id=config.user_id)
    return page
