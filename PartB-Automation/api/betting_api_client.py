"""HTTP client for the sports betting endpoints."""

from __future__ import annotations

from typing import Any, Optional

import requests


class BettingApiClient:
    """Thin wrapper over the sports betting HTTP endpoints."""

    def __init__(
        self,
        base_url: str,
        user_id: str,
        timeout: int = 15,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-user-id": user_id,
        }

    def get_matches(self) -> requests.Response:
        """GET /api/matches — the current match list."""
        return self._session.get(
            f"{self.base_url}/matches",
            headers=self.headers,
            timeout=self.timeout,
        )

    def get_balance(self) -> requests.Response:
        """GET /api/balance — the caller's current balance."""
        return self._session.get(
            f"{self.base_url}/balance",
            headers=self.headers,
            timeout=self.timeout,
        )

    def place_bet(
        self,
        match_id: Any = None,
        selection: Any = None,
        stake: Any = None,
        *,
        payload: Any = "__default__",
        data: Optional[str] = None,
    ) -> requests.Response:
        """POST /api/place-bet with the given fields, or with a raw payload for negative tests."""
        request_kwargs: dict[str, Any] = {
            "headers": self.headers,
            "timeout": self.timeout,
        }
        if data is not None:
            request_kwargs["data"] = data
        else:
            if payload == "__default__":
                payload = {
                    "matchId": match_id,
                    "selection": selection,
                    "stake": stake,
                }
            request_kwargs["json"] = payload

        return self._session.post(
            f"{self.base_url}/place-bet",
            **request_kwargs,
        )

    def reset_balance(self) -> requests.Response:
        """POST /api/reset-balance — restore the caller's balance to the seed value."""
        return self._session.post(
            f"{self.base_url}/reset-balance",
            headers=self.headers,
            timeout=self.timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "BettingApiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
