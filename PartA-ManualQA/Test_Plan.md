# Test Plan — Single Bet Placement

Six prioritized scenarios covering the happy path, negative/validation cases, and boundary conditions for the Single Bet Placement feature. The set is deliberately small — each scenario earns its place either because it protects a financial rule from the specification, breaks a documented user flow, or explores a boundary where product behaviour is easy to get wrong.

**Legend**

| Severity     | Meaning                                                                                          |
| --------------| --------------------------------------------------------------------------------------------------|
| **Critical** | Direct financial loss, data corruption, or revenue blocker. Must pass every release.             |
| **High**     | Breaks a core flow or a documented business rule; customer visible. Must pass before production. |
| **Medium**   | Degrades UX or shows misleading information; workaround exists. Should be fixed soon.            |
| **Low**      | Cosmetic or non-blocking. Tracked, does not gate release.                                        |

---

## TC-01 — Place a valid single bet end-to-end

- **Priority:** Critical
- **Type:** Happy path

**Risk rationale**
This is the core revenue path. If a customer cannot successfully place a single bet, the product has no reason to exist. It also exercises the full stack (match list, bet slip, stake input, payout calculation, `POST /api/place-bet`, receipt, and balance update), so a single failure here surfaces regressions across many components.

**Steps**
1. Open the application with a valid `user-id`.
2. Note the header balance (**B0**).
3. Pick the first UPCOMING football match.
4. Click the HOME odds button; capture the displayed odds (**O**).
5. Verify the bet slip shows the match, HOME selection, and odds **O**.
6. Enter a valid stake of **€5.00**.
7. Verify Potential Payout = **5.00 × O** (rounded to 2 decimals).
8. Click **Place Bet**.

**Expected result**
- Success receipt modal appears with a Bet ID, match name, selection HOME, stake €5.00, odds **O**, potential payout, and a placement timestamp.
- Header balance updates to **B0 − 5.00**.
- Closing the receipt returns the user to an empty bet slip.

---

## TC-02 — Stake boundary, precision, and balance validation

- **Priority:** Critical
- **Type:** Boundary + Negative

**Risk rationale**
Stake bounds and decimal precision are financial rules. If the app accepts stakes below the €1.00 minimum, above the €100.00 maximum, above the customer's available balance, or with more than 2 decimal places, the operator loses control of exposure and audit. Insufficient balance is the most sensitive of these paths — if it is not rejected the customer effectively wagers money they do not have.

**Steps**

Preparation: reset the user's balance via `POST /api/reset-balance` so its value is known. Note the balance as **B**.

For each stake value below, select a valid HOME odds, enter the stake in the bet slip, and attempt to Place Bet:

1. Stake = **0.99** (below the €1.00 minimum)
2. Stake = **1.00** (minimum, accepted)
3. Stake = **100.00** (maximum, accepted)
4. Stake = **100.01** (just above the maximum)
5. Stake = **5.123** (more than 2 decimal places)
6. Stake = **"abc"** (non-numeric)
7. Stake left empty
8. Stake = **B + 0.01** (exceeds available balance)

**Expected result**
- `0.99` — rejected with *"Minimum stake is €1.00"*; no bet placed.
- `1.00` and `100.00` — accepted; bet is placed and balance debited.
- `100.01` — rejected with *"Maximum stake is €100.00"*.
- `5.123` — rejected on precision; input either capped at 2 decimals or Place Bet is blocked with a precision message.
- Non-numeric and empty — Place Bet is disabled; the input rejects non-numeric characters silently.
- `B + 0.01` — rejected with *"Insufficient balance"* at both UI and API; no bet placed; balance remains at **B**.

---

## TC-03 — Bet slip enforces one active selection at a time

- **Priority:** High
- **Type:** Business rule

**Risk rationale**
If old selections linger on the bet slip when a new odds button is clicked, the customer can accidentally place a bet on an outcome they did not intend. This is both a UX and a financial correctness risk, and it is explicitly called out in the specification: *"Selecting a new odds button replaces the previous selection"*.

**Steps**
1. Open the application.
2. On match **A**, click the HOME odds button; verify the bet slip shows exactly one selection: A / HOME.
3. On the same match **A**, click the DRAW odds button; verify the bet slip shows exactly one selection: A / DRAW.
4. On a different match **B**, click the AWAY odds button; verify the bet slip shows exactly one selection: B / AWAY.
5. Click the per-selection remove icon on the bet slip; verify the slip empties.
6. Click a new odds button; verify the slip re-populates with the new single selection.

**Expected result**
- At every step the bet slip contains exactly one active selection.
- The odds and selection type displayed on the slip match the last button clicked.
- Remove All and per-selection remove both clear the slip and return it to the empty state (*"Select odds to place a bet"*).

---

## TC-04 — Error modal handles failed placement (Rebet, Close, X)

- **Priority:** High
- **Type:** Negative / Error handling

**Risk rationale**
When placement fails, the customer needs a clear recovery path. If Rebet does not retry, Close does not clear state, or the X icon behaves inconsistently, users lose trust and abandon the flow. Rebet retrying against a still-broken backend can also create duplicate bets if the retry logic is wrong, which is a financial risk.

**Steps**
1. Configure or simulate a failure path (e.g., stake exceeding the current balance, or backend-forced 500).
2. Select a valid match/HOME, enter a stake, click Place Bet.
3. Verify the error modal is shown with title *"Something went wrong"* and a body explaining the failure.
4. Click **Rebet**; verify placement is retried against the API (observe network) and no new modal instance stacks up.
5. Reproduce step 2. In the error modal, click **Close**; verify the modal closes and the active selection and stake are cleared.
6. Reproduce step 2. In the error modal, click the top-right **X**; verify the same behaviour as Close (modal closes, selection and stake cleared).

**Expected result**
- Rebet closes the modal and issues a fresh `POST /api/place-bet`; no duplicate placement is registered on success.
- Close and the X icon both close the modal and reset the bet slip to the empty state.
- Balance is only debited if a subsequent retry succeeds.

---

## TC-05 — API rejects placement without a valid x-user-id

- **Priority:** High
- **Type:** Negative / API auth

**Risk rationale**
Every endpoint is behind the `x-user-id` header. If the API accepts requests without it, or with an unknown value, an attacker or a broken client can place bets against another user's balance. This is a direct financial and security risk and belongs at the contract layer, not only in the UI.

**Steps**

Using a REST client (or a small script), send `POST /api/place-bet` with a syntactically valid body (real `matchId`, selection HOME, stake 5.00) under three conditions:

1. Do not send the `x-user-id` header at all.
2. Send `x-user-id: ""` (empty string).
3. Send `x-user-id: "user-does-not-exist-123"`.

In each case, capture the HTTP status code and response body.

**Expected result**
- Each request returns HTTP **401**.
- The response body matches the `AuthError` schema with an error code of `missing_user_id` (case 1) or `invalid_user_id` (cases 2 and 3).
- No bet is recorded; a follow-up `GET /api/balance` with the affected user returns the unchanged balance.

---

## TC-06 — Date and odds filters (single day, range, invalid input)

- **Priority:** Medium
- **Type:** Boundary + Filter

**Risk rationale**
Filters shape what a customer can bet on. A silently misapplied date range, or an accepted-but-invalid odds range, can hide matches from the user or expose the wrong ones. Ranges must be inclusive on both ends per the specification, and an invalid odds range (min > max) must give clear feedback rather than a blank list.

**Steps**
1. Apply Date filter = single day (pick a day known to have matches). Verify only that day's matches are listed.
2. Apply Date filter = range (start day **A** to end day **B**, A < B); confirm matches on both A and B are included (inclusive).
3. Apply Odds filter **min = 1.50, max = 2.50**; verify every displayed match has at least one odd within `[1.50, 2.50]`.
4. Apply Odds filter **min = 3.00, max = 2.00** (invalid); verify the app shows a clear invalid-range message and does not silently filter to an empty list.
5. Apply Odds filter **min = 1.00, max = 1000.00** (full range); verify all matches are shown.

**Expected result**
- Date filter is inclusive on both endpoints of a range.
- Odds filter is inclusive; only matches with an odd inside the range remain.
- An invalid odds range surfaces explicit feedback and does not apply the filter.
- Resetting or widening filters restores the full match list.

---

## Execution notes

- **TC-01, TC-02, TC-03** are the top three priorities and are the scenarios run for Part A section 2 (execution results). Defects surfaced during execution are recorded in `Execution_Results_And_Bugs.md`.
- **TC-01** and a portion of **TC-02** are the ones automated in Part B (see the automation framework's `tests/` folder).
- **TC-04** is not automated at this stage because reliably triggering the failure path requires a way to force API errors on demand that the current environment does not expose (see the strategy document for the recommended fix).
