from __future__ import annotations

import pytest

from api.betting_api_client import BettingApiClient


@pytest.mark.api
@pytest.mark.critical
def test_place_bet_rejects_stake_below_minimum(
    api_client: BettingApiClient,
) -> None:
    """The €1 stake floor is a financial rule and must hold at the API too.
    UI validation alone isn't enough — a mobile client or a curl call would bypass it,
    so we lock the rule at the contract with a fast, deterministic test.
    """
    matches_response = api_client.get_matches()
    assert matches_response.status_code == 200, (
        f"GET /api/matches failed with {matches_response.status_code}: "
        f"{matches_response.text[:200]}"
    )
    matches = matches_response.json()
    assert isinstance(matches, list) and matches, "Expected a non-empty match list."
    match_id = matches[0]["id"]

    response = api_client.place_bet(
        match_id=match_id,
        selection="HOME",
        stake=0.99,
    )

    assert response.status_code == 422, (
        f"Expected HTTP 422 for a sub-minimum stake, got {response.status_code}. "
        f"Body: {response.text[:200]}"
    )
    body = response.json()
    assert body.get("error") == "invalid_stake_min", (
        f"Expected error code 'invalid_stake_min', got {body.get('error')!r}. "
        f"Full body: {body}"
    )
    assert body.get("message"), "Expected a non-empty human-readable error message."
