"""Landing page — hosts the match list, bet slip, receipt, and balance header."""

from __future__ import annotations

import re

from selenium.webdriver.common.by import By

from controller.betslip_container import BetslipContainer
from controller.success_modal_controller import SuccessModalController
from controller.upcoming_match import UpcomingMatch
from lib.base_page import BasePage


class HomePage(BasePage):
    """Sports betting landing page."""

    sports_widget = (By.CSS_SELECTOR, ".matchList")
    landed_selector = sports_widget

    balance_header = (By.XPATH, "//*[contains(normalize-space(.), 'Balance:')]")
    betslip_container = (By.CSS_SELECTOR, "#bet-slip-aside")
    success_model_root = (By.CSS_SELECTOR, "#modal-success")

    @property
    def upcoming(self) -> UpcomingMatch:
        """Upcoming-matches list widget."""
        root = self.wait_visible(self.sports_widget)
        return UpcomingMatch(self.driver, root, timeout=self.timeout)

    @property
    def betslip(self) -> BetslipContainer:
        """Right-hand bet slip aside."""
        root = self.wait_visible(self.betslip_container)
        return BetslipContainer(self.driver, root, timeout=self.timeout)

    @property
    def success_modal(self) -> SuccessModalController:
        """Bet-placed receipt modal (only present after a placement)."""
        root = self.wait_visible(self.success_model_root)
        return SuccessModalController(self.driver, root, timeout=self.timeout)

    def balance(self) -> float:
        """Current balance shown in the header, as a float."""
        text = self.get_text(self.balance_header)
        match = re.search(r"-?\d+(?:[.,]\d+)?", text)
        if not match:
            raise ValueError(f"Cannot parse header balance from {text!r}")
        return float(match.group(0).replace(",", "."))
