# Sports Betting Automation

Focused automation suite for the Sporty Group Single Bet Placement feature.
The project protects the most valuable end-to-end journey (a customer placing a bet)
and a critical API validation rule (stake below minimum is rejected with a semantic
error).

## Stack

- Python 3.10+
- Selenium WebDriver 4 (Chrome, latest desktop)
- webdriver-manager (auto-provisions the correct ChromeDriver)
- Pytest 8
- requests
- python-dotenv (optional, for local `.env` overrides)

## Project Layout

```
03_AUTOMATION/
├── api/                 # HTTP client for the betting API
├── controller/          # Component + workflow controllers (bet slip, sports widget, ...)
├── lib/                 # Base classes for pages and components
├── page/                # Top-level page objects (rooted at the WebDriver)
├── tests/               # Pytest tests + fixtures
├── utility/             # Configuration and WebDriver factory
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

The architecture separates responsibilities:

- `page.HomePage` receives the Selenium `WebDriver` and finds component roots.
- Component controllers (`SportsWidget`, `BetslipContainer`, `SuccessModalController`)
  receive `driver` plus their own root `WebElement` so all searches are scoped.
- `BetPlacementController` is a workflow controller that receives `HomePage` and
  orchestrates the sports widget, bet slip and success modal.
- `api.BettingApiClient` wraps the HTTP contract so tests read like business scenarios,
  not raw `requests` calls.

## Setup

```powershell
# From the 03_AUTOMATION folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want to override the defaults (for example,
run a different `USER_ID` or point at a different environment).

## Running the Tests

```powershell
# Full suite
pytest

# Only UI or only API
pytest -m ui
pytest -m api

# Headless Chrome
$env:HEADLESS = "1"; pytest -m ui

# Single test
pytest tests/test_place_bet_api.py::test_place_bet_rejects_stake_below_minimum
```

## Automated Coverage

| Layer | Test | Why it is automated |
|---|---|---|
| UI (E2E) | `tests/test_single_bet_ui.py::test_successful_single_bet_placement` | Protects the highest-value customer journey. If this breaks, no one can place a bet. |
| API | `tests/test_place_bet_api.py::test_place_bet_rejects_stake_below_minimum` | Protects a critical financial validation rule directly at the contract, independent of the UI. |

Each test carries an inline docstring explaining its rationale.

## Notes for Reviewers

- The suite is designed so that the framework, not the number of tests, is the artifact.
  Adding more UI or API tests is a matter of dropping new `test_*.py` files or extending
  the existing page/controller/API-client classes.
- The API client resets the user balance before the UI test so the bet placement journey
  is deterministic on repeated runs.
- Selectors were verified against the live application (`?user-id=<candidate>`) and
  centralized in the corresponding controller class.
