"""Bet-placed receipt modal."""

from __future__ import annotations

import re

from selenium.webdriver.common.by import By

from lib.base_control import BaseControl


_NUMERIC_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _extract_number(text: str) -> float:
    match = _NUMERIC_RE.search(text or "")
    if not match:
        raise ValueError(f"No numeric content in {text!r}")
    return float(match.group(0))


class SuccessModalController(BaseControl):
    """The 'Bet Placed' receipt modal."""

    ROOT_SELECTOR = (By.CSS_SELECTOR, "#modal-success")

    BET_ID = (By.CSS_SELECTOR, "#modal-success-bet-id")
    MATCH = (By.CSS_SELECTOR, "#modal-success-match")
    STAKE = (By.CSS_SELECTOR, "#modal-success-stake")
    ODDS = (By.CSS_SELECTOR, "#modal-success-odds")
    PAYOUT = (By.CSS_SELECTOR, "#modal-success-payout")
    PLACED_AT = (By.CSS_SELECTOR, "#modal-success-placed-at")
    CLOSE_BUTTON = (By.CSS_SELECTOR, "#modal-success-close")
    CLOSE_X = (By.CSS_SELECTOR, "#modal-success-close-x")

    def wait_visible_modal(self) -> None:
        """Fail loudly if the modal isn't visible."""
        if not self.is_displayed():
            raise AssertionError("Success modal is not displayed.")

    @property
    def bet_id(self) -> str:
        """Bet reference number shown on the receipt."""
        return self.get_text(self.BET_ID)

    @property
    def match(self) -> str:
        """Match string on the receipt (home vs away)."""
        return self.get_text(self.MATCH)

    @property
    def stake(self) -> float:
        """Stake amount on the receipt as a float."""
        return _extract_number(self.get_text(self.STAKE))

    @property
    def odds(self) -> float:
        """Odds decimal on the receipt."""
        return _extract_number(self.get_text(self.ODDS))

    @property
    def payout(self) -> float:
        """Potential payout on the receipt as a float."""
        return _extract_number(self.get_text(self.PAYOUT))

    @property
    def placed_at(self) -> str:
        """Placement timestamp shown on the receipt."""
        return self.get_text(self.PLACED_AT)

    def close(self) -> None:
        """Click the primary CLOSE button."""
        self.click(self.CLOSE_BUTTON)

    def close_via_x(self) -> None:
        """Click the top-right X icon."""
        self.click(self.CLOSE_X)
