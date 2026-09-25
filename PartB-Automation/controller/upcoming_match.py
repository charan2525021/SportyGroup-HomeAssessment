"""Wraps the list of upcoming match cards on the home page."""

from typing import List

from .match import Match

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from lib.base_control import BaseControl


class UpcomingMatch(BaseControl):
    """The upcoming-matches list on the home page."""

    def match(self) -> List[Match]:
        """Every match card on the page, wrapped as a Match control."""
        return self.map_elements(
            selector=".matchCard",
            ctor=Match,
        )
