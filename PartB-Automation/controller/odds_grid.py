"""1 / X / 2 odds buttons on a match card."""

from __future__ import annotations

from enum import Enum

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from lib.base_control import BaseControl


class MatchResult(Enum):
    """Match outcome the customer can bet on."""

    HOME = "home"
    DRAW = "draw"
    AWAY = "away"


class OddsGrid(BaseControl):
    """The 1 / X / 2 odds buttons attached to a single match."""

    ODDS_BUTTONS = (By.CSS_SELECTOR, "button[id^='odds-']")

    def _button(self, result: MatchResult) -> WebElement:
        """Odds button for the given outcome."""
        suffix = f"-{result.value}"
        for btn in self.find_all(self.ODDS_BUTTONS):
            if (btn.get_attribute("id") or "").endswith(suffix):
                return btn
        raise LookupError(f"No odds button found for {result.name}")

    def odds_value(self, result: MatchResult) -> float:
        """Decimal odds shown on the button for the given outcome."""
        text = (self._button(result).text or "").replace("\n", " ").strip()
        tokens = text.split()
        if not tokens:
            raise ValueError("Odds button text is empty")
        return float(tokens[-1])

    def selection(self, result: MatchResult) -> WebElement:
        """Clickable odds button for the given outcome."""
        return self._button(result)
