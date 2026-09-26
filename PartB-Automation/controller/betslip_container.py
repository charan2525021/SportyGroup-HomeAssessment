"""Right-hand bet slip: selection, stake entry, payout, place-bet."""

from __future__ import annotations

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from controller.betreceipt import BetReceipt
from lib.base_control import BaseControl


def _parse_currency(text: str) -> float:
    return float(text.replace(",", "").replace("₹", "").strip())


class BetslipContainer(BaseControl):
    """The bet slip aside: current selection, stake, payout, and place-bet."""

    stake_input = (By.CSS_SELECTOR, "#bet-slip-stake-input")
    placebet_button = (By.CSS_SELECTOR, "#bet-slip-place-bet")
    remove_all_button = (By.CSS_SELECTOR, "#bet-slip-remove-all")
    selection_remove_button = (By.CSS_SELECTOR, "#bet-slip-selection-remove")

    odds_label = (By.XPATH, ".//*[starts-with(normalize-space(.), 'Odds:')]")
    total_stake_row = (
        By.XPATH,
        ".//*[normalize-space(.)='Total Stake']/following-sibling::*[1]",
    )
    potential_payout_row = (
        By.XPATH,
        ".//*[normalize-space(.)='Potential Payout']/following-sibling::*[1]",
    )

    success_modal = (By.CSS_SELECTOR, "#modal-success")

    selected_match_team = (By.CSS_SELECTOR, ".betSelectionTeams")
    selected_match_market = (By.CSS_SELECTOR, ".betSelectionMarket")

    def has_active_selection(self) -> bool:
        """True if the slip currently holds a selection."""
        return self.exists(self.stake_input)

    def wait_for_selection(self) -> None:
        """Wait until the slip shows a stake input (a selection was made)."""
        self.wait_visible(self.stake_input)

    def wait_for_empty(self) -> None:
        """Wait until the slip clears its stake input."""
        self.wait_gone(self.stake_input)

    def enter_stake(self, amount: str | float | int) -> None:
        """Type the stake amount into the input."""
        self.type_text(self.stake_input, str(amount))

    def remove_all(self) -> None:
        """Click Remove All if it is currently present on the slip."""
        if self.exists(self.remove_all_button):
            self.click(self.remove_all_button)

    def remove_current_selection(self) -> None:
        """Click the per-selection remove icon if it is present."""
        if self.exists(self.selection_remove_button):
            self.click(self.selection_remove_button)

    def displayed_odds(self) -> float:
        """Odds decimal shown next to the current selection."""
        text = self.get_text(self.odds_label)
        parts = text.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Unable to parse odds label {text!r}")
        return float(parts[1].strip())

    def total_stake(self) -> float:
        """Total Stake amount shown on the slip."""
        return _parse_currency(self.get_text(self.total_stake_row))

    def potential_payout(self) -> float:
        """Potential Payout amount shown on the slip."""
        return _parse_currency(self.get_text(self.potential_payout_row))

    def selected_match(self) -> str:
        """Home vs Away label of the current selection."""
        return self.get_text(self.selected_match_team)

    def selected_market(self) -> str:
        """Market label of the current selection (e.g. 'Match Winner: Home')."""
        return self.get_text(self.selected_match_market)

    def place_bet_enabled(self) -> bool:
        """True if the Place Bet button is displayed and enabled."""
        try:
            button = self.find(self.placebet_button)
        except Exception:
            return False
        class_attr = button.get_attribute("class") or ""
        return button.is_enabled() and "placeBetButtonDisabled" not in class_attr
    
    def place_bet(self) -> BetReceipt:
        """Click Place Bet, wait for the receipt modal, and return it."""
        self.wait_clickable(self.placebet_button).click()
        wait = WebDriverWait(self.driver, self.timeout)

        def _resolve(drv):
            try:
                el = drv.find_element(*self.success_modal)
                return el if el.is_displayed() else False
            except Exception:
                return False

        modal_root = wait.until(_resolve, message="Success modal did not appear")
        return BetReceipt(self.driver, modal_root, timeout=self.timeout)
