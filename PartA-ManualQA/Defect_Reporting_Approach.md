# Defect Reporting --- Approach

I reported five defects from the testing. I focused on issues that
affect bet placement, account balance, or information shown to the
customer, rather than adding minor visual issues just to increase the
defect count.

## What I focused on

-   **Financial impact:** Could the issue cause an incorrect payout or
    allow a bet that the customer cannot afford?
-   **Customer trust:** Is the app showing information that could
    mislead the customer?
-   **User flow:** Does a key action fail without making it clear that
    something went wrong?
-   **Specification:** Does the behaviour go against a rule in the
    requirements?

## Defects reported

  -----------------------------------------------------------------------
  ID                      Severity                Reason
  ----------------------- ----------------------- -----------------------
  BUG-01                  Critical                Winning bets are paid
                                                  using the wrong amount.
                                                  This could cause a
                                                  financial loss on every
                                                  winning settlement and
                                                  does not match the
                                                  quote shown before the
                                                  bet is placed.

  BUG-03                  Critical                The API allows bets
                                                  that take the
                                                  customer's balance
                                                  below zero. This means
                                                  a bet can be accepted
                                                  even when the customer
                                                  does not have enough
                                                  funds.

  BUG-02                  High                    The balance shown in
                                                  the app does not update
                                                  correctly. Customers
                                                  may rely on an outdated
                                                  amount when deciding
                                                  whether to place
                                                  another bet.

  BUG-04                  High                    Clicking an odds button
                                                  appears to select it,
                                                  but nothing is added to
                                                  the bet slip. There is
                                                  no error message to
                                                  explain what happened.

  BUG-05                  Medium                  The page says there are
                                                  "103 matches," but the
                                                  match grid is empty.
                                                  The count and the
                                                  content shown on the
                                                  page do not agree.
  -----------------------------------------------------------------------

## Issue noted for triage

The success modal displays the match as **"Away vs Home"** instead of
**"Home vs Away."** This is visible in the same screenshot as BUG-01. I
have not logged it as a separate defect yet, but it may need its own
ticket if the receipt is considered the official record of the bet.

I also left out spacing and animation issues that do not affect how the
customer uses the app.

## How I tested

1.  Ran the Critical and High priority scenarios from the test plan
    (TC-01, TC-02 and TC-03). This is where I found BUG-01, BUG-02 and
    BUG-03.
2.  Did a short exploratory session around the same flow, including
    repeated odds clicks, filter edge cases and low-balance checks. This
    is where I found BUG-04 and BUG-05.

The `Defect_Report.xlsx` file in this folder contains the defect
details. This note explains how I selected and reported them.
