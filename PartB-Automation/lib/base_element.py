"""Locator + wait helpers shared by pages and controls."""

from __future__ import annotations

from typing import Tuple, Union

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[str, str]
SearchContext = Union[WebDriver, WebElement]


class BaseElement:
    """Foundation for pages and controls; owns a driver and a search context."""

    DEFAULT_TIMEOUT = 15

    def __init__(
        self,
        driver: WebDriver,
        parent: SearchContext | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.driver = driver
        self.parent: SearchContext = parent if parent is not None else driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator: Locator) -> WebElement:
        """First descendant matching the locator, scoped to the current context."""
        return self.parent.find_element(*locator)

    def find_all(self, locator: Locator) -> list[WebElement]:
        """All descendants matching the locator."""
        return self.parent.find_elements(*locator)

    def exists(self, locator: Locator) -> bool:
        """True if the locator resolves right now, without waiting."""
        try:
            self.parent.find_element(*locator)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def wait_visible(self, locator: Locator) -> WebElement:
        """Wait until the element is present and displayed, then return it."""
        return self.wait.until(
            lambda _drv: self._resolve_visible(locator),
            message=f"Element {locator!r} not visible within {self.timeout}s",
        )  # type: ignore

    def wait_clickable(self, locator: Locator) -> WebElement:
        """Wait until the element is displayed and enabled, then return it."""
        return self.wait.until(
            lambda _drv: self._resolve_clickable(locator),
            message=f"Element {locator!r} not clickable within {self.timeout}s",
        )  # type: ignore

    def wait_gone(self, locator: Locator) -> bool:
        """Wait until the element is no longer displayed."""
        try:
            return self.wait.until(
                lambda _drv: not self._resolve_visible(locator),
                message=f"Element {locator!r} still present after {self.timeout}s",
            )
        except TimeoutException:
            return False

    def click(self, locator: Locator) -> None:
        """Wait for the element to be clickable, then click it."""
        self.wait_clickable(locator).click()

    def type_text(self, locator: Locator, value: str) -> None:
        """Clear the field and type the value into it."""
        element = self.wait_visible(locator)
        element.clear()
        element.send_keys(str(value))

    def get_text(self, locator: Locator) -> str:
        """Trimmed visible text of the element."""
        return self.wait_visible(locator).text.strip()

    def _resolve_visible(self, locator: Locator) -> WebElement | bool:
        try:
            element = self.parent.find_element(*locator)
            return element if element.is_displayed() else False
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def _resolve_clickable(self, locator: Locator) -> WebElement | bool:
        try:
            element = self.parent.find_element(*locator)
            if element.is_displayed() and element.is_enabled():
                return element
            return False
        except (NoSuchElementException, StaleElementReferenceException):
            return False
