# Strategy and Recommendations

## Why I chose these two tests for automation

I committed two automated tests:

-   **`test_bet_placement_ui1`** --- end-to-end UI test for placing a
    valid single bet.
-   **`test_place_bet_rejects_stake_below_minimum`** --- API test for
    validating the minimum stake.

I chose these because they cover two important areas of a betting
product: the customer's bet-placement journey and the financial rules
enforced by the API. They also have different purposes, so there is
little overlap and the maintenance effort should stay manageable.

  -----------------------------------------------------------------------
  Candidate               Picked?                 Reason
  ----------------------- ----------------------- -----------------------
  E2E happy path (bet     Yes                     This covers the main
  placement)                                      customer journey. If
                                                  bet placement stops
                                                  working, customers
                                                  cannot place bets. The
                                                  test checks the match
                                                  list, bet slip, stake
                                                  input, placement
                                                  request and receipt
                                                  modal in one run.

  API stake-below-minimum Yes                     This checks a financial
                                                  rule directly at the
                                                  API layer. It runs in
                                                  about 1.5 seconds and
                                                  is not tied to UI
                                                  changes, so it can
                                                  catch backend
                                                  validation regressions
                                                  independently of the
                                                  E2E test.

  Bet slip "one active    Manual for now          This is mainly a state
  selection" (TC-03)                              check. A component test
                                                  using Playwright or
                                                  Storybook would be a
                                                  more efficient option
                                                  than adding another
                                                  Selenium test. I'll
                                                  keep it manual until
                                                  that test layer is
                                                  available.

  Error modal Rebet /     Manual                  These flows need the
  Close / X (TC-04)                               API to fail in a
                                                  controlled way. The
                                                  current environment
                                                  does not provide a
                                                  reliable way to trigger
                                                  that failure, and
                                                  stubbing responses in
                                                  Selenium could make the
                                                  test flaky.

  API auth 401 checks     Manual                  These checks are
                                                  useful, but
                                                  authentication
                                                  middleware is not
                                                  expected to change
                                                  often. Other API tests
                                                  would also fail if the
                                                  authentication layer
                                                  had a broader problem.

  Filter behaviour        Manual                  This is medium priority
  (TC-06)                                         and largely visual, so
                                                  manual testing is
                                                  sufficient for now. It
                                                  can be revisited when
                                                  visual regression
                                                  tooling is in place.

  Full stake boundary     Deferred                This would be a good
  matrix                                          next step:
                                                  parameterised API tests
                                                  for minimum, maximum,
                                                  precision and
                                                  insufficient-balance
                                                  cases. For this pass, I
                                                  wanted to prove the
                                                  automation approach
                                                  with two focused tests
                                                  rather than add a large
                                                  number of tests
                                                  straight away.
  -----------------------------------------------------------------------

## What I kept as manual testing

-   **Exploratory testing around bet placement:** A tester can try
    different actions and notice unexpected behaviour that a fixed
    script may not cover. BUG-04 is an example: the issue was noticed
    during a short exploratory session, while a script might need many
    repeated clicks to reproduce it.
-   **Error-modal flows (Rebet / Close / X):** These depend on
    controllable backend failures. Until we can trigger those failures
    reliably, keeping the flows manual avoids introducing flaky
    browser-level stubs.
-   **Currency, timestamps and copy:** These are sensitive to locale and
    presentation. For this exercise, a human review is a practical way
    to check that the displayed values and wording make sense.
-   **Cross-browser and mobile:** These were outside the scope of the
    specification. I would first make sure the desktop Chrome flow is
    stable before expanding the browser and device coverage.

## Recommendations if the suite is expanded

### 1. Add the tests to CI/CD before increasing test coverage

The next step should be to make sure the tests run regularly. An
automated test that is not part of the normal development process can
easily be missed.

I recommend adding a GitHub Actions workflow that:

-   Runs the API tests on every pull request, since they are fast and
    deterministic and should finish in under two minutes.
-   Runs the full UI and API suite when changes are merged to `main`.
-   Runs the full suite nightly as an additional check.

This keeps pull-request feedback quick while still giving the team a
broader regression check. The current framework already supports
headless Chrome; the main additions are the workflow YAML and a secret
for the candidate user ID.

### 2. Improve test data before enabling parallel runs

The current suite uses one shared `user-id` and resets the balance
through the API before each UI run. That works when tests run one at a
time on one machine, but parallel pipeline runs could interfere with
each other. For example, one run could reset the balance while another
run is placing a bet.

I recommend three changes:

-   **Use a separate user ID for each run:** Generate a fresh `user-id`
    for each pipeline run, or take one from a managed pool. Pass it
    through the fixtures instead of hard-coding a shared value. This
    will isolate test state and make parallel execution safer.
-   **Use snapshotted fixtures for the catalogue:** Save a known-good
    `/api/matches` response as JSON mock data. Tests that depend on
    specific matches, teams or odds can use that fixture instead of
    relying on whatever the live backend happens to return.
-   **Mock the API for failure paths and less common states:** Keep the
    live backend for the happy path, but add a way to simulate responses
    and states that are difficult to produce in the test environment.

For the UI tests, this could be done with Selenium CDP request
interception or by moving the UI tier to Playwright, which has built-in
route mocking. This would make it possible to:

-   Return `500`, `409` or `422` responses from `/api/place-bet` and
    test the error modal actions (Rebet / Close / X). These flows are
    manual today because the backend cannot be made to fail on demand
    reliably.
-   Simulate less common catalogue states, such as an empty match list,
    a single match, or boundary odds like `1.01` and `1000.00`, which
    may not appear in the live seed data.
-   Check the exact request payload sent to the API. This can help catch
    client-side contract changes, such as a renamed field or a number
    being sent as a string.

For API tests, a mock HTTP server such as `pytest-httpserver` or
WireMock, driven by the OpenAPI schema, could provide the same benefit.
The API validation tests could then run without depending on the
deployed backend.

The approach I would use is to keep **live data for the smoke suite**,
where the goal is to prove that the real system works, and use **mock
data for focused tests**, where the goal is to check individual rules in
isolation. Using both for their intended purposes gives the team
realistic end-to-end coverage as well as fast, repeatable checks.

### 3. Expand the Test Pyramid with lower-level tests

The defects found during this exercise suggest that the next coverage
improvements should not all be additional end-to-end tests. Several
issues were related to the success modal and bet-slip state, which could
be checked at a lower level.

I recommend adding:

-   **Component tests** for the bet slip and success modal. These could
    exercise the relevant UI and state without requiring a full
    end-to-end run. They may have caught BUG-01 and could help cover the
    behaviour behind BUG-04.
-   **Contract tests** against the OpenAPI schema. These would detect
    unintended changes to `PlaceBetResponse` early, without waiting for
    an end-to-end test to expose the mismatch.

I would keep E2E tests for the smoke suite and the key customer journeys
that must continue to work. Other checks can be placed lower in the Test
Pyramid, where they are generally faster and easier to diagnose.

## Specification point to confirm with product

There is an inconsistency in the specification around the minimum stake.
The business rules section says **€1.00**, while the validation table
lists **€1.01**.

For this exercise, I used €1.00 based on the business rules section.
Before making this check a firm automated requirement, the product owner
should confirm which value is correct. A short regular QA and product
review of specification questions would also help resolve similar
ambiguities earlier.
