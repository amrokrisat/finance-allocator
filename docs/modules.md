# Module Definitions

## Orchestration

Purpose:
Coordinate a full planning run from raw inputs to stored results.

Responsibilities:

- load user profile and active financial state
- call intake normalization
- request strategy selection
- invoke allocation, debt, and savings/investing modules
- assemble explanation output
- persist run summary and line items

Key outputs:

- allocation plan
- explanation messages
- warnings and unmet-target indicators

## Intake

Purpose:
Convert raw user data into validated, normalized planning models.

Responsibilities:

- validate required fields
- normalize all income and expense frequencies to monthly values
- classify expenses as essential or flexible
- compute available balances and target metadata for goals
- reject invalid or contradictory inputs

Key outputs:

- planning snapshot
- normalized monthly cash-flow inputs

## Strategy

Purpose:
Choose the rule set that governs the allocation waterfall.

Responsibilities:

- select a default profile such as conservative, balanced, or aggressive
- apply user overrides
- provide thresholds for emergency savings and debt handling
- define ordering and caps for each destination bucket

Key outputs:

- strategy configuration
- ordered allocation rules

## Allocation

Purpose:
Distribute available monthly cash across categories according to the selected strategy.

Responsibilities:

- reserve required obligations first
- compute discretionary cash
- apply waterfall ordering
- enforce caps and stop conditions
- emit line items with reason codes

Key outputs:

- category allocations
- leftover cash indicator
- unmet need indicator

## Debt

Purpose:
Model debt obligations and recommend extra payments.

Responsibilities:

- compute minimum monthly obligations
- rank debts for extra payoff using MVP rule set
- support at least avalanche ordering by APR
- expose payoff-target metadata for explanations

Key outputs:

- minimum payment totals
- prioritized debt list
- extra-payoff recommendations

## Savings / Investing

Purpose:
Recommend contributions to emergency savings, sinking funds, retirement, brokerage, and short-term goals.

Responsibilities:

- compute emergency fund target from monthly essentials
- compute sinking fund monthly need from goal date and target amount
- support retirement match logic when provided by the user
- separate tax-advantaged and taxable investing destinations

Key outputs:

- destination-level recommended contributions
- target progress metadata

## Testing

Purpose:
Protect the correctness of financial logic.

Responsibilities:

- unit-test normalization and allocation rules
- unit-test debt prioritization and target calculations
- integration-test one full planning scenario
- capture regression fixtures for edge cases

Priority coverage:

- insufficient income
- no debt
- high-interest debt present
- emergency fund below threshold
- over-subscribed goals
- zero discretionary cash

## Evaluation

Purpose:
Explain and assess whether the generated plan is reasonable.

Responsibilities:

- attach rationale strings to allocation decisions
- report which goals were partially funded or unfunded
- surface heuristic checks for suspicious outputs
- provide machine-checkable result summaries for tests

Key outputs:

- explanation payload
- warnings
- evaluation summary
