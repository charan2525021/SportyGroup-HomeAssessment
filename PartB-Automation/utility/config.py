"""Runtime config from env vars, with a .env fallback."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    _DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"
    if _DOTENV_PATH.exists():
        load_dotenv(_DOTENV_PATH)
except ImportError:
    pass


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Config:
    """Immutable snapshot of the runtime settings."""

    base_url: str
    user_id: str
    headless: bool
    ui_timeout: int
    api_timeout: int

    @property
    def api_base_url(self) -> str:
        """Base URL for the API (``base_url`` + ``/api``)."""
        return f"{self.base_url.rstrip('/')}/api"

    @property
    def app_url(self) -> str:
        """URL that opens the app with the current user-id."""
        return f"{self.base_url.rstrip('/')}/?user-id={self.user_id}"


def load_config() -> Config:
    """Read settings from environment variables into a Config."""
    return Config(
        base_url=os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app"),
        user_id=os.getenv("USER_ID", "candidate-Bemplv1NTNMQ"),
        headless=_get_bool("HEADLESS", default=False),
        ui_timeout=_get_int("UI_TIMEOUT", default=15),
        api_timeout=_get_int("API_TIMEOUT", default=15),
    )


CONFIG: Config = load_config()
