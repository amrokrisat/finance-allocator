# Architecture

## Overview

The MVP uses a simple three-layer setup:

- Next.js frontend for forms, authentication screens, and scenario/result views.
- Python backend for financial logic, orchestration, and persistence.
- Postgres for durable storage of user inputs and allocation runs.

The backend is the source of truth for all financial calculations. The frontend should not contain business rules beyond display formatting and client-side input ergonomics.

## System Boundaries

### Frontend

Responsible for:

- local auth screens
- guided intake forms
- scenario submission
- displaying allocation recommendations
- showing rationale and warnings returned by the backend

Not responsible for:

- deciding allocation order
- debt prioritization rules
- emergency fund target calculation
- tax-aware investment logic

### Backend

Responsible for:

- local auth APIs
- input validation and normalization
- strategy selection
- monthly allocation logic
- debt payoff recommendation logic
- savings and investing recommendation logic
- plan explanation and persistence

### Database

Responsible for:

- storing user data
- storing financial state snapshots used for a plan run
- storing plan outputs and rationale metadata

## Proposed Runtime Shape

### Frontend

- `app/`: route handlers and pages
- `components/`: reusable UI pieces
- `lib/`: API client, auth helpers, formatting helpers

### Backend

- `api/`: HTTP routes and dependency wiring
- `schemas/`: request and response shapes
- `models/`: ORM models mirroring persisted tables
- `services/`: pure or near-pure business modules
- `db/`: session setup and repository helpers
- `core/`: config, security, and shared utilities

## Core Allocation Flow

1. Load user profile and active financial inputs.
2. Normalize all amounts to monthly values.
3. Compute required obligations first.
4. Determine available discretionary cash.
5. Apply strategy waterfall in a fixed order.
6. Produce recommended contributions for each allocation bucket.
7. Persist the run and return explanation data.

## Recommended MVP Waterfall

The default waterfall should be intentionally simple:

1. Required monthly expenses
2. Minimum debt payments
3. Starter emergency savings if below threshold
4. Employer-match retirement contribution if applicable
5. High-priority short-term goals
6. Additional high-interest debt payoff
7. Full emergency fund target
8. Sinking funds
9. Retirement beyond match
10. Taxable brokerage investing

This order is an assumption for MVP and should stay configurable through strategy profiles.

## Non-Goals For MVP

- live bank aggregation
- automatic transaction categorization
- advanced tax optimization
- Monte Carlo projections
- household collaboration
- real-time market data
