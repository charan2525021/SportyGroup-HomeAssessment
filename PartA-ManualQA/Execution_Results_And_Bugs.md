# Execution Results and Defect Report

## Execution summary

The three highest-priority scenarios from the test plan were executed against the deployed application at `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`, followed by a short exploratory pass around the bet placement flow.

| Test case | Priority | Result | Defects found |
|---|---|---|---|
| TC-01 — Valid single bet end-to-end | Critical | Fail | BUG-01, BUG-02 |
| TC-02 — Stake boundary and balance validation | Critical | Fail | BUG-03 |
| TC-03 — One active selection on the bet slip | High | Pass | — |
| Exploratory around the placement flow | — | — | BUG-04, BUG-05 |

Five defects were logged in total. The report is deliberately short — each defect earns its place either because it breaks a financial rule from the specification, breaks a documented user flow, or contradicts something the product told the customer a second earlier. Padding the list with cosmetic issues would only dilute the signal.

---

## Defects

### BUG-01 — Success modal Potential Payout is calculated as `stake × 2` instead of `stake × odds`

- **Severity:** Critical
- **Scenario:** TC-01 (single bet placement happy path)

**Reproduction steps**
1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`.
2. Select the first upcoming match (Manchester Utd vs Chelsea) and click the HOME odds button (`1 / 2.45`).
3. Verify the Bet Slip shows the selection with **Odds: 2.45**.
4. Enter stake = **5** in the Bet Slip.
5. Confirm the Bet Slip shows Potential Payout = **€12.25** (correct: 5 × 2.45).
6. Click **Place Bet**.
7. Observe the Potential Payout on the success modal.

**Expected vs actual**
- **Expected:** Potential Payout on the success modal = **€12.25** (stake × odds), matching the value quoted on the Bet Slip before placement.
- **Actual:** Potential Payout on the success modal = **€10.00**, which equals `5 × 2`. The modal ignores the actual odds (still displayed as 2.45 on the same modal) and applies a hardcoded multiplier of 2.

**Business impact**
Customer is quoted €12.25 before placement and shown €10.00 on the receipt for the same bet. If settlement follows the receipt, the operator underpays every winning bet — direct financial loss and consumer-trust/regulatory risk.

**Evidence**
See [`screenshots/Issue1.bmp`](screenshots/Issue1.bmp) — captures both the Bet Slip pre-placement showing **€12.25** for stake €5.00 at odds 2.45, and the success modal showing €5.00 stake, 2.45 odds, but **€10.00** payout.

---

### BUG-02 — Balance in header and Bet Slip does not refresh after a successful Place Bet

- **Severity:** High
- **Scenario:** TC-01 (exploratory follow-up during execution)

**Reproduction steps**
1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`.
2. Record the current balance shown in the header **and** in the Bet Slip aside (value = **B**).
3. Select the first upcoming match, click the HOME odds (Manchester Utd, 2.45).
4. Enter stake = **5** and click **Place Bet**.
5. When the success modal appears, look at the header balance and the "Balance:" line at the top of the Bet Slip aside (behind the modal).
6. Close the modal and observe the same two values again.

**Expected vs actual**
- **Expected:** Both the header balance and the Bet Slip "Balance:" line should immediately show **B − 5.00** as soon as the placement succeeds.
- **Actual:** Both values remain at **B**. The deducted balance is only visible after a manual page reload or another triggering action.

**Business impact**
Customer sees a stale, inflated balance right after a bet is placed. This can lead them to place further bets thinking they still have the full amount, causing surprise "insufficient balance" errors or over-commitment. Trust in the financial display is a core requirement for a betting product.

**Evidence**
See [`screenshots/Issue2.bmp`](screenshots/Issue2.bmp) — shows the success modal for a €2.00 bet with the header and Bet Slip both stuck at **Balance: €111.00**, followed by a new bet in progress on the same page where the header is still €111.00.

---

### BUG-03 — Place Bet accepted when stake exceeds available balance (user can go into negative balance)

- **Severity:** Critical
- **Scenario:** TC-02 (insufficient balance validation)

**Reproduction steps**
1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`.
2. Note the current balance; if it is >= €200, `POST /api/reset-balance` first so the balance is around €125.
3. Select the first upcoming match and click the HOME odds (Manchester Utd, 2.45).
4. Enter stake = **100** and click **Place Bet**. The bet is accepted; success modal shown.
5. Close the modal, click another odds button.
6. Enter stake = **100** and click **Place Bet**.
7. Reload the page and observe the balance in the header and Bet Slip.

**Expected vs actual**
- **Expected:** Per Feature Specification section 4.1 (*"Stake — Must not exceed available balance — UI + API — Show/reject as insufficient balance"*) and section 4.4, the second placement must be rejected at both UI and API with an *"Insufficient balance"* message. Balance must never become negative.
- **Actual:** Both €100 placements succeed. After refresh the header and Bet Slip show **Balance: −€91.00**. No *"Insufficient balance"* error is shown at any point.

**Business impact**
Direct financial exposure — the operator effectively extends unsecured credit to the customer with zero underwriting. Regulatory risk in most jurisdictions (unlicensed extension of credit) and an obvious abuse vector for bad actors chaining bets against a small balance.

**Evidence**
See [`screenshots/Issue3.bmp`](screenshots/Issue3.bmp) — home page after refresh showing **Balance: −€91.00** in the header and at the top of the Bet Slip aside.

---

### BUG-04 — Odds selection not added to Bet Slip (intermittent)

- **Severity:** High
- **Scenario:** Exploratory (bet slip selection behaviour)

**Reproduction steps**
1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`.
2. Click any odds button on any upcoming match — for example Real Madrid HOME (`1 / 1.85`).
3. Observe the odds button state and the Bet Slip aside.
4. Repeat across several matches/outcomes; the defect is intermittent and may need multiple attempts before it surfaces.

**Expected vs actual**
- **Expected:** Per Feature Specification 2.1 and 2.2, every accepted odds click must immediately populate the Bet Slip with that selection (match, market, odds, stake input, Place Bet button).
- **Actual:** The odds button occasionally transitions to the red **selected** state (the `oddsButtonSelected` visual style is applied) but the Bet Slip aside remains in the empty state — counter shows **0**, placeholder *"Select odds to place a bet"* still displayed.

**Business impact**
Silent failure at the entry point of the whole betting flow. When it happens the customer cannot proceed to place a bet and has no error to react to — they either give up (lost revenue) or retry, risking accidental double-selection on a different outcome.

**Evidence**
See [`screenshots/Issue4.bmp`](screenshots/Issue4.bmp) — Real Madrid HOME odds highlighted in the red selected state while the Bet Slip aside shows the empty state.

**Note**
Intermittent — suggest triager retry across several matches. Recommend checking DevTools console/network for a failed request when it occurs.

---

### BUG-05 — "Showing X matches" count does not update when Date or Odds filter is applied

- **Severity:** Medium
- **Scenario:** Exploratory (filter behaviour)

**Reproduction steps**
1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Bemplv1NTNMQ`.
2. Note the total match count in the header — e.g. *"Showing 103 matches"*.
3. Open the **Odds** filter, set a narrow range that will exclude most matches (e.g. **9.02 – 10.00**), click **Apply**.
4. Observe the match list and the count text.
5. Repeat with the **Date** filter set to a single day that has few or no matches.

**Expected vs actual**
- **Expected:** Per Feature Specification 2.6, once a valid filter is applied, the header count should reflect the number of matches actually rendered — *"Showing 0 matches"* when the filter yields no results, or the true filtered count otherwise.
- **Actual:** The match list correctly filters (empty grid when the filter yields no matches), but the count text remains at the pre-filter total. In the captured case the odds range **9.02 – 10.00** shows zero matches but the header still reads *"Showing 103 matches"*.

**Business impact**
Contradictory information in the UI — the customer sees *"103 matches"* while looking at an empty grid. Users lose confidence in the filter feature and, by association, in any other numeric value the product displays.

**Evidence**
See [`screenshots/Issue5.bmp`](screenshots/Issue5.bmp) — Odds filter set to **9.02 – 10.00**, empty match list, header still displays *"Showing 103 matches"*.

---

## Not filed (on purpose)

- The success modal shows the match as *"Away vs Home"* instead of *"Home vs Away"*. Visible in the same screenshot as BUG-01. If the receipt is the authoritative record of what the customer bought, this deserves its own ticket — flagging here for triage rather than inflating the count.
- Cosmetic spacing and animation issues that do not change what the customer can do.

## Reporting philosophy

> *"You are not scored on bug count. You are scored on the quality of your reports and whether you catch the high impact issues."*

Every defect above passes at least one of these tests: **financial exposure**, **regulatory or trust risk**, **silent failure**, or **direct contradiction of the specification**. Two of the five (BUG-01, BUG-03) sit directly on the operator's money.
