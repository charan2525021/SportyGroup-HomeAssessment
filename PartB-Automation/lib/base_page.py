"""Base for full-page objects rooted at the WebDriver."""

from __future__ import annotations

from typing import ClassVar, Optional
from urllib.parse import urlencode

from selenium.webdriver.remote.webdriver import WebDriver

from lib.base_element import BaseElement, Locator


class BasePage(BaseElement):
    """Full-page search context — rooted at the WebDriver."""

    landed_selector: ClassVar[Optional[Locator]] = None

    def __init__(
        self,
        driver: WebDriver,
        timeout: int = BaseElement.DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(driver=driver, parent=driver, timeout=timeout)

    def navigate_to(self, url: str) -> None:
        """Load a URL in the current browser tab."""
        self.driver.get(url)

    def open(self, base_url: str, user_id: str) -> "BasePage":
        """Open the app for the given user-id and wait until the page has landed."""
        url = f"{base_url.rstrip('/')}/?{urlencode({'user-id': user_id})}"
        self.navigate_to(url)
        if self.landed_selector is not None:
            self.wait_visible(self.landed_selector)
        return self

    @property
    def current_url(self) -> str:
        """URL currently shown in the browser."""
        return self.driver.current_url

    @property
    def title(self) -> str:
        """Browser tab title."""
        return self.driver.title
