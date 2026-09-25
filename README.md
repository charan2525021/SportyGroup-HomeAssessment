# QA Engineer Home Assignment — Single Bet Placement

Submission for the QA Engineer take-home assignment. The feature under test is the **Single Bet Placement** flow on the sports betting web application at `https://qae-assignment-tau.vercel.app/`.

## Repository layout

```
HomeAssessment/
├── README.md                            # you are here
├── PartA-ManualQA/
│   ├── Test_Plan.md                     # six prioritized test scenarios (canonical)
│   ├── Test_Plan.docx                   # Word version of the same plan
│   ├── Test_Scenarios.xlsx              # Excel matrix of the six scenarios
│   ├── Execution_Results_And_Bugs.md    # execution notes and defect reports
│   ├── Defect_Report.xlsx               # Excel matrix of all defects (same content)
│   ├── Defect_Reporting_Approach.md     # short note on how defects were selected
│   └── screenshots/                     # BUG-01 to BUG-05 evidence images
│       ├── Issue1.bmp                   # BUG-01 (payout mismatch)
│       ├── Issue2.bmp                   # BUG-02 (balance not refreshing)
│       ├── Issue3.bmp                   # BUG-03 (negative balance)
│       ├── Issue4.bmp                   # BUG-04 (odds selection not added)
│       └── Issue5.bmp                   # BUG-05 (filter count mismatch)
├── PartB-Automation/                    # Python 3 + Selenium + Pytest framework
│   ├── README.md                        # setup and run instructions
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── conftest.py
│   ├── api/                             # HTTP client for the betting API
│   ├── controller/                      # component controllers (bet slip, match card, odds grid...)
│   ├── lib/                             # base element / control / page
│   ├── page/                            # top-level page objects (HomePage)
│   ├── tests/                           # 2 automated tests (E2E UI + API)
│   └── utility/                         # config and driver factory
└── PartC-Strategy/
    └── Strategy_And_Recommendations.md  # short strategy note
```

## Deliverables

| Deliverable | Primary (markdown) | Also provided |
|---|---|---|
| Test plan (6 prioritized scenarios) | [`PartA-ManualQA/Test_Plan.md`](PartA-ManualQA/Test_Plan.md) | [`Test_Plan.docx`](PartA-ManualQA/Test_Plan.docx), [`Test_Scenarios.xlsx`](PartA-ManualQA/Test_Scenarios.xlsx) |
| Execution results and 5 defect reports | [`PartA-ManualQA/Execution_Results_And_Bugs.md`](PartA-ManualQA/Execution_Results_And_Bugs.md) | [`Defect_Report.xlsx`](PartA-ManualQA/Defect_Report.xlsx), [`Defect_Reporting_Approach.md`](PartA-ManualQA/Defect_Reporting_Approach.md), [`screenshots/`](PartA-ManualQA/screenshots) |
| Automation framework + 2 automated tests | [`PartB-Automation/`](PartB-Automation/) | — |
| Strategy and recommendations | [`PartC-Strategy/Strategy_And_Recommendations.md`](PartC-Strategy/Strategy_And_Recommendations.md) | — |

## Stack

- Python 3.10+
- Selenium WebDriver 4 (Chrome, latest desktop)
- webdriver-manager (auto-provisions the correct ChromeDriver)
- Pytest 8
- requests (API testing)
- python-dotenv (optional, for local `.env` overrides)

## Running the automation

```powershell
cd PartB-Automation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Full suite (UI + API)
pytest

# Only the API tier (fast — ~2 seconds)
pytest -m api

# Only the UI tier
pytest -m ui

# Headless Chrome
$env:HEADLESS = "1"; pytest
```

The candidate user id defaults to `candidate-Bemplv1NTNMQ`. Override via `.env` (copy `.env.example` first) or environment variables (`BASE_URL`, `USER_ID`, `HEADLESS`, `UI_TIMEOUT`, `API_TIMEOUT`).

See [`PartB-Automation/README.md`](PartB-Automation/README.md) for the full framework guide.

## Automated coverage

| Layer | Test | Rationale |
|---|---|---|
| UI (E2E) | `tests/test_single_bet_ui1.py::test_bet_placement_ui1` | Core revenue path. If placing a single bet breaks, the product stops earning. |
| API | `tests/test_place_bet_api.py::test_place_bet_rejects_stake_below_minimum` | The €1 stake floor is a financial rule and must hold at the API even if the UI is bypassed. |

Full rationale for these two picks (and what was deliberately left as manual) is in [`PartC-Strategy/Strategy_And_Recommendations.md`](PartC-Strategy/Strategy_And_Recommendations.md).

## Notes for the reviewer

- The report is deliberately short. Five defects — not fifty — chosen for high impact. The Part A bug document opens with the criteria used to decide what gets filed and what does not.
- The framework is optimized for **maintainability and extensibility** over raw test count. Adding more scenarios is a matter of dropping a new `test_*.py` and reusing the existing controllers.
- The strategy note explains where the framework goes next if this were to scale — CI/CD wiring, test data strategy including mocking for failure paths, and where to broaden the pyramid.
