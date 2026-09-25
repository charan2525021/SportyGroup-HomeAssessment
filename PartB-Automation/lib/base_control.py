"""Base for a control scoped to one component's WebElement."""

from __future__ import annotations

from typing import Callable, TypeVar

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from lib.base_element import BaseElement


T = TypeVar("T")


class BaseControl(BaseElement):
    """Component-scoped search context — rooted at a specific WebElement."""

    def __init__(
        self,
        driver: WebDriver,
        parent: WebElement,
        timeout: int = BaseElement.DEFAULT_TIMEOUT,
    ) -> None:
        if parent is None:
            raise ValueError("BaseControl requires a non-null root WebElement.")
        super().__init__(driver=driver, parent=parent, timeout=timeout)

    def is_displayed(self) -> bool:
        """True if the component's root element is currently visible."""
        try:
            return self.parent.is_displayed()  # type: ignore
        except Exception:
            return False

    def scroll_into_view(self) -> None:
        """Scroll the component's root element into the viewport."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.parent,
        )

    def map_elements(
        self,
        selector: str,
        ctor: Callable[..., T],
    ) -> list[T]:
        """Wrap every element matching ``selector`` into ``ctor`` and return the list."""
        elements = self.wait.until(
            lambda _driver: self.parent.find_elements(
                By.CSS_SELECTOR,
                selector,
            ) or False,
            message=f"Elements matching {selector!r} not found within "
            f"{self.timeout}s",
        )

        return [
            ctor(driver=self.driver, parent=element, timeout=self.timeout)
            for element in elements
        ]
