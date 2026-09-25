from __future__ import annotations

import pytest
from controller.odds_grid import MatchResult
from page.home_page import HomePage


@pytest.mark.ui
@pytest.mark.critical
def test_bet_placement_ui1(home_page: HomePage) -> None:
    """Core revenue path. If placing a single bet breaks, the product stops earning.
    Covers match list, bet slip, stake input, payout, place-bet, and receipt in one flow,
    so one regression here surfaces breakage across most of the feature.
    """
    match = home_page.upcoming.match()[0]
    participants = match.participants()
    odds_grid = match.option()
    selection_button = odds_grid.selection(MatchResult.HOME)
    expected_odds = odds_grid.odds_value(MatchResult.HOME)
    selection_button.click()
    betslip = home_page.betslip
    betslip.wait_for_selection()
    assert betslip.selected_match() ==  f"{participants['home']} vs {participants['away']}"
    assert betslip.displayed_odds() == pytest.approx(expected_odds)
    assert betslip.selected_market() == f"Match Winner: {MatchResult.HOME.value.capitalize()}"
    stake = 1.0
    betslip.enter_stake(stake)
    expected_payout = round(stake * expected_odds, 2)
    receipt = betslip.place_bet()
    assert receipt.bet_id
    assert participants["home"] in receipt.match
    assert participants["away"] in receipt.match
    assert receipt.stake == pytest.approx(stake)
    assert receipt.odds == pytest.approx(expected_odds)
    assert receipt.payout == pytest.approx(expected_payout),(f"Potential Payout is showing wrong after placebet Expected payout {expected_payout} from betslip, but got {receipt.payout} in placedBet")
    assert receipt.placed_at
    receipt.close()